"""
Stripe payment service
"""
import stripe
from typing import Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeService:
    """Stripe payment service"""

    def __init__(self):
        self.price_ids = {
            "starter": settings.STRIPE_PRICE_STARTER,
            "professional": settings.STRIPE_PRICE_PROFESSIONAL,
            "agency": settings.STRIPE_PRICE_AGENCY
        }

    async def create_checkout_session(
        self,
        user_id: str,
        email: str,
        tier: str,
        trial_days: int = 14
    ) -> Optional[str]:
        """
        Create a Stripe checkout session for subscription
        """
        try:
            price_id = self.price_ids.get(tier)

            if not price_id:
                logger.error(f"Invalid tier: {tier}")
                return None

            session = stripe.checkout.Session.create(
                customer_email=email,
                mode='subscription',
                line_items=[{
                    'price': price_id,
                    'quantity': 1
                }],
                success_url=f'{settings.FRONTEND_URL}/dashboard?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{settings.FRONTEND_URL}/pricing',
                subscription_data={
                    'trial_period_days': trial_days,
                    'metadata': {
                        'user_id': user_id
                    }
                },
                metadata={
                    'user_id': user_id,
                    'tier': tier
                }
            )

            return session.url

        except Exception as e:
            logger.error(f"Error creating checkout session: {e}")
            return None

    async def create_customer_portal_session(
        self,
        customer_id: str
    ) -> Optional[str]:
        """
        Create a customer portal session for managing subscription
        """
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id,
                return_url=f'{settings.FRONTEND_URL}/dashboard'
            )

            return session.url

        except Exception as e:
            logger.error(f"Error creating portal session: {e}")
            return None

    async def cancel_subscription(
        self,
        subscription_id: str
    ) -> bool:
        """
        Cancel a subscription
        """
        try:
            stripe.Subscription.delete(subscription_id)
            return True

        except Exception as e:
            logger.error(f"Error canceling subscription: {e}")
            return False


# Create singleton instance
stripe_service = StripeService()
