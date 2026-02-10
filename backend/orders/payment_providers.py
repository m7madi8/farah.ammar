"""
Payment provider integration: Stripe PaymentIntent and PayPal (placeholder).
All provider calls are here; never trust frontend for payment verification.
"""
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)


def get_stripe_client_secret(amount: Decimal, currency: str, payment_id: int, order_public_id: str, metadata: dict = None):
    """
    Create Stripe PaymentIntent and return client_secret for frontend.
    Amount from order total only (server-side); Stripe expects smallest unit (cents).
    """
    try:
        import stripe
        from django.conf import settings
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    except (ImportError, AttributeError) as e:
        logger.warning("Stripe not configured: %s", e)
        return None, None

    if not stripe.api_key:
        return None, None

    # Stripe amounts in smallest currency unit (cents for USD/EUR; agorot for ILS)
    amount_int = int(amount * 100)
    if amount_int <= 0:
        raise ValueError("Amount must be positive")

    metadata = metadata or {}
    metadata.setdefault('payment_id', str(payment_id))
    metadata.setdefault('order_public_id', order_public_id)

    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_int,
            currency=(currency or 'ils').lower(),
            automatic_payment_methods={'enabled': True},
            metadata=metadata,
        )
        return intent.client_secret, intent.id
    except Exception as e:
        logger.exception("Stripe PaymentIntent create failed: %s", e)
        raise


def get_paypal_payment_url(amount: Decimal, currency: str, payment_id: int, order_public_id: str, return_url: str, cancel_url: str):
    """
    Create PayPal order and return approval URL for frontend.
    Placeholder: implement with paypalrestsdk or PayPal Orders API.
    """
    logger.info("PayPal integration placeholder for order %s amount %s", order_public_id, amount)
    # In production: create order via PayPal API, return links[rel=approve].href
    return None


def verify_stripe_webhook(raw_body: bytes, signature_header: str):
    """
    Verify Stripe webhook signature and return event dict.
    Raises ValueError if signature invalid. Never trust payload without verification.
    """
    try:
        import stripe
        from django.conf import settings
        stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', None)
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', None)
    except (ImportError, AttributeError):
        raise ValueError("Stripe or webhook secret not configured")

    if not webhook_secret:
        raise ValueError("STRIPE_WEBHOOK_SECRET not set")

    try:
        event = stripe.Webhook.construct_event(raw_body, signature_header, webhook_secret)
        return event
    except stripe.SignatureVerificationError as e:
        logger.warning("Stripe webhook signature verification failed: %s", e)
        raise ValueError("Invalid signature")
    except Exception as e:
        logger.exception("Stripe webhook construct_event failed: %s", e)
        raise
