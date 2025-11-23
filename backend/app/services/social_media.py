"""Social media integration service for posting content."""
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import asyncio
import httpx

from app.core.logging import logger
from app.core.exceptions import ServiceException


class SocialPlatform(str, Enum):
    """Supported social media platforms."""

    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"


class TwitterService:
    """Service for posting to Twitter/X using v2 API."""

    def __init__(self, api_key: str, api_secret: str, access_token: str, access_secret: str):
        """
        Initialize Twitter API client.

        Args:
            api_key: Twitter API key
            api_secret: Twitter API secret
            access_token: User access token
            access_secret: User access token secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_secret = access_secret
        self.base_url = "https://api.twitter.com/2"

    async def post_tweet(
        self, text: str, media_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Post a tweet.

        Args:
            text: Tweet text (max 280 characters)
            media_ids: List of uploaded media IDs

        Returns:
            Dictionary with tweet_id and tweet_url
        """
        try:
            # OAuth 1.0a authentication headers
            from requests_oauthlib import OAuth1Session

            oauth = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_secret,
            )

            payload = {"text": text[:280]}  # Truncate to 280 chars

            if media_ids:
                payload["media"] = {"media_ids": media_ids}

            response = oauth.post(f"{self.base_url}/tweets", json=payload)

            if response.status_code == 201:
                data = response.json()
                tweet_id = data["data"]["id"]
                tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

                logger.info(f"Tweet posted successfully: {tweet_id}")
                return {"tweet_id": tweet_id, "tweet_url": tweet_url}
            else:
                error_msg = response.json().get("detail", "Unknown error")
                raise ServiceException(f"Twitter API error: {error_msg}")

        except Exception as e:
            logger.error(f"Failed to post tweet: {str(e)}")
            raise ServiceException(f"Twitter post failed: {str(e)}")

    async def delete_tweet(self, tweet_id: str) -> bool:
        """
        Delete a tweet.

        Args:
            tweet_id: Tweet ID to delete

        Returns:
            True if successful
        """
        try:
            from requests_oauthlib import OAuth1Session

            oauth = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_secret,
            )

            response = oauth.delete(f"{self.base_url}/tweets/{tweet_id}")

            if response.status_code == 200:
                logger.info(f"Tweet deleted: {tweet_id}")
                return True
            else:
                raise ServiceException(f"Failed to delete tweet: {response.text}")

        except Exception as e:
            logger.error(f"Failed to delete tweet: {str(e)}")
            raise ServiceException(f"Twitter delete failed: {str(e)}")


class FacebookService:
    """Service for posting to Facebook pages using Graph API."""

    def __init__(self, access_token: str, page_id: str):
        """
        Initialize Facebook Graph API client.

        Args:
            access_token: Page access token
            page_id: Facebook page ID
        """
        self.access_token = access_token
        self.page_id = page_id
        self.base_url = "https://graph.facebook.com/v18.0"

    async def post_to_page(
        self, message: str, link: Optional[str] = None, image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post to Facebook page.

        Args:
            message: Post message
            link: Optional link to share
            image_url: Optional image URL

        Returns:
            Dictionary with post_id
        """
        try:
            async with httpx.AsyncClient() as client:
                endpoint = f"{self.base_url}/{self.page_id}/feed"

                data = {
                    "message": message,
                    "access_token": self.access_token,
                }

                if link:
                    data["link"] = link

                if image_url:
                    # For images, use photos endpoint instead
                    endpoint = f"{self.base_url}/{self.page_id}/photos"
                    data["url"] = image_url

                response = await client.post(endpoint, data=data)
                response.raise_for_status()

                result = response.json()
                post_id = result.get("id", "")

                logger.info(f"Facebook post created: {post_id}")
                return {"post_id": post_id}

        except httpx.HTTPStatusError as e:
            logger.error(f"Facebook API error: {e.response.text}")
            raise ServiceException(f"Facebook post failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {str(e)}")
            raise ServiceException(f"Facebook post failed: {str(e)}")

    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a Facebook post.

        Args:
            post_id: Facebook post ID

        Returns:
            True if successful
        """
        try:
            async with httpx.AsyncClient() as client:
                endpoint = f"{self.base_url}/{post_id}"

                params = {"access_token": self.access_token}

                response = await client.delete(endpoint, params=params)
                response.raise_for_status()

                logger.info(f"Facebook post deleted: {post_id}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete Facebook post: {str(e)}")
            raise ServiceException(f"Facebook delete failed: {str(e)}")


class LinkedInService:
    """Service for posting to LinkedIn using v2 API."""

    def __init__(self, access_token: str, person_urn: str):
        """
        Initialize LinkedIn API client.

        Args:
            access_token: LinkedIn access token
            person_urn: LinkedIn person URN (e.g., urn:li:person:ABC123)
        """
        self.access_token = access_token
        self.person_urn = person_urn
        self.base_url = "https://api.linkedin.com/v2"

    async def create_post(
        self, text: str, article_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a LinkedIn post.

        Args:
            text: Post text
            article_url: Optional article URL to share

        Returns:
            Dictionary with post_id
        """
        try:
            async with httpx.AsyncClient() as client:
                endpoint = f"{self.base_url}/ugcPosts"

                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                }

                payload = {
                    "author": self.person_urn,
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": text},
                            "shareMediaCategory": "NONE",
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
                }

                # Add article if URL provided
                if article_url:
                    payload["specificContent"]["com.linkedin.ugc.ShareContent"][
                        "shareMediaCategory"
                    ] = "ARTICLE"
                    payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                        {
                            "status": "READY",
                            "originalUrl": article_url,
                        }
                    ]

                response = await client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()

                result = response.json()
                post_id = result.get("id", "")

                logger.info(f"LinkedIn post created: {post_id}")
                return {"post_id": post_id}

        except httpx.HTTPStatusError as e:
            logger.error(f"LinkedIn API error: {e.response.text}")
            raise ServiceException(f"LinkedIn post failed: {e.response.text}")
        except Exception as e:
            logger.error(f"Failed to post to LinkedIn: {str(e)}")
            raise ServiceException(f"LinkedIn post failed: {str(e)}")

    async def delete_post(self, post_urn: str) -> bool:
        """
        Delete a LinkedIn post.

        Args:
            post_urn: LinkedIn post URN

        Returns:
            True if successful
        """
        try:
            async with httpx.AsyncClient() as client:
                endpoint = f"{self.base_url}/ugcPosts/{post_urn}"

                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                }

                response = await client.delete(endpoint, headers=headers)
                response.raise_for_status()

                logger.info(f"LinkedIn post deleted: {post_urn}")
                return True

        except Exception as e:
            logger.error(f"Failed to delete LinkedIn post: {str(e)}")
            raise ServiceException(f"LinkedIn delete failed: {str(e)}")


class SocialMediaManager:
    """Unified manager for all social media platforms."""

    def __init__(self):
        """Initialize social media manager."""
        self.services: Dict[str, Any] = {}

    def add_twitter(
        self, api_key: str, api_secret: str, access_token: str, access_secret: str
    ):
        """Add Twitter service."""
        self.services[SocialPlatform.TWITTER] = TwitterService(
            api_key, api_secret, access_token, access_secret
        )

    def add_facebook(self, access_token: str, page_id: str):
        """Add Facebook service."""
        self.services[SocialPlatform.FACEBOOK] = FacebookService(access_token, page_id)

    def add_linkedin(self, access_token: str, person_urn: str):
        """Add LinkedIn service."""
        self.services[SocialPlatform.LINKEDIN] = LinkedInService(
            access_token, person_urn
        )

    async def post_to_platform(
        self,
        platform: SocialPlatform,
        text: str,
        link: Optional[str] = None,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post content to a specific platform.

        Args:
            platform: Social media platform
            text: Post text
            link: Optional link to share
            media_url: Optional media URL

        Returns:
            Platform-specific response
        """
        if platform not in self.services:
            raise ServiceException(f"Platform {platform} not configured")

        service = self.services[platform]

        try:
            if platform == SocialPlatform.TWITTER:
                return await service.post_tweet(text)
            elif platform == SocialPlatform.FACEBOOK:
                return await service.post_to_page(text, link=link, image_url=media_url)
            elif platform == SocialPlatform.LINKEDIN:
                return await service.create_post(text, article_url=link)
            else:
                raise ServiceException(f"Platform {platform} not supported")

        except Exception as e:
            logger.error(f"Failed to post to {platform}: {str(e)}")
            raise

    async def post_to_multiple(
        self,
        platforms: List[SocialPlatform],
        text: str,
        link: Optional[str] = None,
        media_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Post content to multiple platforms simultaneously.

        Args:
            platforms: List of platforms to post to
            text: Post text
            link: Optional link to share
            media_url: Optional media URL

        Returns:
            Dictionary mapping platform to result
        """
        results = {}
        tasks = []

        for platform in platforms:
            if platform in self.services:
                task = self.post_to_platform(platform, text, link, media_url)
                tasks.append((platform, task))

        # Execute all posts concurrently
        for platform, task in tasks:
            try:
                result = await task
                results[platform] = {"success": True, "data": result}
            except Exception as e:
                results[platform] = {"success": False, "error": str(e)}
                logger.error(f"Failed to post to {platform}: {str(e)}")

        return results

    async def delete_from_platform(
        self, platform: SocialPlatform, post_id: str
    ) -> bool:
        """
        Delete a post from a specific platform.

        Args:
            platform: Social media platform
            post_id: Platform-specific post ID

        Returns:
            True if successful
        """
        if platform not in self.services:
            raise ServiceException(f"Platform {platform} not configured")

        service = self.services[platform]

        try:
            if platform == SocialPlatform.TWITTER:
                return await service.delete_tweet(post_id)
            elif platform == SocialPlatform.FACEBOOK:
                return await service.delete_post(post_id)
            elif platform == SocialPlatform.LINKEDIN:
                return await service.delete_post(post_id)
            else:
                raise ServiceException(f"Platform {platform} not supported")

        except Exception as e:
            logger.error(f"Failed to delete from {platform}: {str(e)}")
            raise
