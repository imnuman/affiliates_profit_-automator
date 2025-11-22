"""
Webhook endpoints
"""
from fastapi import APIRouter, Request, HTTPException
from app.config import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/clickbank/ipn")
async def clickbank_ipn(request: Request):
    """
    ClickBank Instant Payment Notification webhook
    """
    # TODO: Implement ClickBank IPN verification and processing
    data = await request.form()
    logger.info(f"Received ClickBank IPN: {data}")

    return {"status": "received"}


@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    Stripe webhook for subscription events
    """
    # TODO: Implement Stripe webhook verification and processing
    payload = await request.body()
    logger.info("Received Stripe webhook")

    return {"status": "received"}
