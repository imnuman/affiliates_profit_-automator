"""
Email service using Postmark
"""
from postmarker.core import PostmarkClient
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Email service"""

    def __init__(self):
        if settings.POSTMARK_API_KEY:
            self.client = PostmarkClient(server_token=settings.POSTMARK_API_KEY)
        else:
            self.client = None
            logger.warning("Postmark API key not configured")

    async def send_welcome_email(self, to_email: str, full_name: str):
        """Send welcome email to new user"""
        if not self.client:
            logger.info(f"Would send welcome email to {to_email}")
            return

        try:
            self.client.emails.send(
                From=settings.POSTMARK_FROM_EMAIL,
                To=to_email,
                Subject=f"Welcome to {settings.APP_NAME}!",
                HtmlBody=f"""
                <h1>Welcome {full_name}!</h1>
                <p>Thank you for signing up for {settings.APP_NAME}.</p>
                <p>Your 14-day free trial has started. Start exploring the platform and create your first campaign!</p>
                <p>If you have any questions, feel free to reach out to our support team.</p>
                <p>Best regards,<br>The {settings.APP_NAME} Team</p>
                """,
                MessageStream='outbound'
            )

            logger.info(f"Welcome email sent to {to_email}")

        except Exception as e:
            logger.error(f"Error sending welcome email: {e}")

    async def send_content_ready_notification(
        self,
        to_email: str,
        content_title: str,
        content_id: str
    ):
        """Send notification when AI content is generated"""
        if not self.client:
            logger.info(f"Would send content ready notification to {to_email}")
            return

        try:
            self.client.emails.send(
                From=settings.POSTMARK_FROM_EMAIL,
                To=to_email,
                Subject="Your content is ready!",
                HtmlBody=f"""
                <h1>Your content is ready!</h1>
                <p>The AI has finished generating: <strong>{content_title}</strong></p>
                <p><a href="{settings.FRONTEND_URL}/content/{content_id}">View your content</a></p>
                """,
                MessageStream='outbound'
            )

            logger.info(f"Content ready notification sent to {to_email}")

        except Exception as e:
            logger.error(f"Error sending content notification: {e}")


# Create singleton instance
email_service = EmailService()
