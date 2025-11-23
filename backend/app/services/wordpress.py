"""WordPress publishing service using XML-RPC."""
from typing import Optional, Dict, Any, List
from datetime import datetime
import xmlrpc.client
from urllib.parse import urlparse

from app.core.logging import logger
from app.core.exceptions import ServiceException


class WordPressService:
    """Service for publishing content to WordPress sites via XML-RPC."""

    def __init__(self, site_url: str, username: str, password: str):
        """
        Initialize WordPress XML-RPC client.

        Args:
            site_url: WordPress site URL (e.g., https://example.com)
            username: WordPress username
            password: WordPress application password or password
        """
        self.site_url = site_url.rstrip("/")
        self.username = username
        self.password = password

        # Construct XML-RPC endpoint
        self.xmlrpc_url = f"{self.site_url}/xmlrpc.php"

        try:
            self.client = xmlrpc.client.ServerProxy(
                self.xmlrpc_url, allow_none=True, use_builtin_types=True
            )
        except Exception as e:
            logger.error(f"Failed to initialize WordPress XML-RPC client: {str(e)}")
            raise ServiceException(f"WordPress connection failed: {str(e)}")

    async def verify_connection(self) -> bool:
        """
        Verify connection to WordPress site.

        Returns:
            True if connection is successful
        """
        try:
            # Call wp.getUsersBlogs to verify credentials
            blogs = self.client.wp.getUsersBlogs(self.username, self.password)
            logger.info(f"WordPress connection verified for {self.site_url}")
            return True
        except xmlrpc.client.Fault as e:
            logger.error(f"WordPress XML-RPC fault: {e.faultString}")
            raise ServiceException(f"WordPress authentication failed: {e.faultString}")
        except Exception as e:
            logger.error(f"WordPress connection error: {str(e)}")
            raise ServiceException(f"WordPress connection error: {str(e)}")

    async def create_post(
        self,
        title: str,
        content: str,
        status: str = "draft",
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        featured_image_url: Optional[str] = None,
        excerpt: Optional[str] = None,
        custom_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new WordPress post.

        Args:
            title: Post title
            content: Post content (HTML)
            status: Post status (draft, publish, pending, private)
            categories: List of category names
            tags: List of tag names
            featured_image_url: URL of featured image
            excerpt: Post excerpt
            custom_fields: Dictionary of custom field key-value pairs

        Returns:
            Dictionary with post_id and post_url
        """
        try:
            # Prepare post data
            post_data = {
                "post_type": "post",
                "post_status": status,
                "post_title": title,
                "post_content": content,
            }

            if excerpt:
                post_data["post_excerpt"] = excerpt

            # Handle categories
            if categories:
                category_ids = []
                for category_name in categories:
                    # Get or create category
                    cat_id = await self._get_or_create_category(category_name)
                    if cat_id:
                        category_ids.append(cat_id)
                if category_ids:
                    post_data["terms"] = {"category": category_ids}

            # Handle tags
            if tags:
                post_data["terms_names"] = {"post_tag": tags}

            # Handle custom fields
            if custom_fields:
                post_data["custom_fields"] = [
                    {"key": key, "value": value}
                    for key, value in custom_fields.items()
                ]

            # Create the post
            post_id = self.client.wp.newPost(
                0,  # Blog ID (0 for single site)
                self.username,
                self.password,
                post_data,
            )

            logger.info(f"WordPress post created: {post_id}")

            # Set featured image if provided
            if featured_image_url and post_id:
                await self._set_featured_image(post_id, featured_image_url)

            # Get post URL
            post = self.client.wp.getPost(
                0, self.username, self.password, post_id, ["link"]
            )

            return {"post_id": post_id, "post_url": post.get("link", "")}

        except xmlrpc.client.Fault as e:
            logger.error(f"WordPress post creation fault: {e.faultString}")
            raise ServiceException(f"Failed to create WordPress post: {e.faultString}")
        except Exception as e:
            logger.error(f"WordPress post creation error: {str(e)}")
            raise ServiceException(f"WordPress post creation failed: {str(e)}")

    async def update_post(
        self,
        post_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        status: Optional[str] = None,
        categories: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> bool:
        """
        Update an existing WordPress post.

        Args:
            post_id: WordPress post ID
            title: New post title
            content: New post content
            status: New post status
            categories: New list of category names
            tags: New list of tag names

        Returns:
            True if update was successful
        """
        try:
            post_data = {}

            if title is not None:
                post_data["post_title"] = title

            if content is not None:
                post_data["post_content"] = content

            if status is not None:
                post_data["post_status"] = status

            if categories:
                category_ids = []
                for category_name in categories:
                    cat_id = await self._get_or_create_category(category_name)
                    if cat_id:
                        category_ids.append(cat_id)
                if category_ids:
                    post_data["terms"] = {"category": category_ids}

            if tags:
                post_data["terms_names"] = {"post_tag": tags}

            # Update the post
            result = self.client.wp.editPost(
                0, self.username, self.password, post_id, post_data
            )

            logger.info(f"WordPress post updated: {post_id}")
            return result

        except xmlrpc.client.Fault as e:
            logger.error(f"WordPress post update fault: {e.faultString}")
            raise ServiceException(f"Failed to update WordPress post: {e.faultString}")
        except Exception as e:
            logger.error(f"WordPress post update error: {str(e)}")
            raise ServiceException(f"WordPress post update failed: {str(e)}")

    async def delete_post(self, post_id: int) -> bool:
        """
        Delete a WordPress post.

        Args:
            post_id: WordPress post ID

        Returns:
            True if deletion was successful
        """
        try:
            result = self.client.wp.deletePost(
                0, self.username, self.password, post_id
            )
            logger.info(f"WordPress post deleted: {post_id}")
            return result
        except xmlrpc.client.Fault as e:
            logger.error(f"WordPress post deletion fault: {e.faultString}")
            raise ServiceException(f"Failed to delete WordPress post: {e.faultString}")
        except Exception as e:
            logger.error(f"WordPress post deletion error: {str(e)}")
            raise ServiceException(f"WordPress post deletion failed: {str(e)}")

    async def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get all categories from WordPress site.

        Returns:
            List of categories with id, name, slug, etc.
        """
        try:
            categories = self.client.wp.getTerms(
                0, self.username, self.password, "category"
            )
            return categories
        except Exception as e:
            logger.error(f"Failed to get WordPress categories: {str(e)}")
            return []

    async def _get_or_create_category(self, category_name: str) -> Optional[int]:
        """
        Get category ID by name, or create it if it doesn't exist.

        Args:
            category_name: Category name

        Returns:
            Category ID or None
        """
        try:
            # Try to get existing category
            categories = await self.get_categories()
            for cat in categories:
                if cat.get("name", "").lower() == category_name.lower():
                    return int(cat.get("term_id", 0))

            # Create new category if not found
            new_cat_id = self.client.wp.newTerm(
                0,
                self.username,
                self.password,
                {"name": category_name, "taxonomy": "category"},
            )

            logger.info(f"Created new WordPress category: {category_name}")
            return int(new_cat_id)

        except Exception as e:
            logger.error(f"Failed to get/create category '{category_name}': {str(e)}")
            return None

    async def _set_featured_image(self, post_id: int, image_url: str) -> bool:
        """
        Set featured image for a post from URL.

        Args:
            post_id: WordPress post ID
            image_url: URL of the image

        Returns:
            True if successful
        """
        try:
            # Note: This requires uploading the image first
            # For now, we'll use a custom field to store the URL
            # In production, you'd want to download and upload the image

            self.client.wp.editPost(
                0,
                self.username,
                self.password,
                post_id,
                {
                    "custom_fields": [
                        {"key": "featured_image_url", "value": image_url}
                    ]
                },
            )

            logger.info(f"Set featured image URL for post {post_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to set featured image: {str(e)}")
            return False

    async def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a WordPress post by ID.

        Args:
            post_id: WordPress post ID

        Returns:
            Post data dictionary or None
        """
        try:
            post = self.client.wp.getPost(0, self.username, self.password, post_id)
            return post
        except Exception as e:
            logger.error(f"Failed to get WordPress post {post_id}: {str(e)}")
            return None

    async def get_posts(
        self, number: int = 10, offset: int = 0, status: str = "any"
    ) -> List[Dict[str, Any]]:
        """
        Get a list of WordPress posts.

        Args:
            number: Number of posts to retrieve
            offset: Offset for pagination
            status: Post status filter

        Returns:
            List of post dictionaries
        """
        try:
            filter_data = {
                "number": number,
                "offset": offset,
                "post_status": status,
            }

            posts = self.client.wp.getPosts(
                0, self.username, self.password, filter_data
            )
            return posts
        except Exception as e:
            logger.error(f"Failed to get WordPress posts: {str(e)}")
            return []
