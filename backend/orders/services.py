"""
Order and payment services: checkout (validate cart, create order, payment intent),
webhook (verify signature, update order & payment, deduct stock with idempotency).
All sensitive operations run inside database transactions.
Stock is deducted only in webhook after payment confirmation — never at checkout.
"""
import logging
import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.conf import settings

from accounts.models import Address
from products.models import Product
from products.signals import log_stock_change

from .models import Order, OrderItem, Payment, Coupon

logger = logging.getLogger(__name__)

# Session key for cart: { product_id: quantity }
CART_SESSION_KEY = 'cart'


def get_cart(request):
    """Return cart dict from session: { product_id: quantity }."""
    return request.session.get(CART_SESSION_KEY) or {}


def get_cart_response(request):
    """Build cart payload for API: items (with product detail), subtotal, item_count."""
    cart = get_cart(request)
    items = []
    subtotal = Decimal('0.00')
    product_ids = [int(pid) for pid in cart if int(cart.get(pid, 0)) > 0]
    if not product_ids:
        return {'items': [], 'subtotal': '0.00', 'item_count': 0}
    products = Product.objects.filter(id__in=product_ids).in_bulk()
    for pid in product_ids:
        qty = int(cart[str(pid)])
        product = products.get(pid)
        if not product:
            continue
        unit = product.discount_price if (
            product.discount_price is not None and product.discount_price < product.price
        ) else product.price
        total = unit * qty
        subtotal += total
        items.append({
            'product_id': product.id,
            'slug': product.slug,
            'name_en': product.name_en,
            'name_ar': product.name_ar or '',
            'price': str(product.price),
            'discount_price': str(product.discount_price) if product.discount_price else None,
            'quantity': qty,
            'unit_price': str(unit),
            'total': str(total),
        })
    return {
        'items': items,
        'subtotal': str(subtotal),
        'item_count': sum(int(cart[str(pid)]) for pid in product_ids),
    }


def set_cart(request, cart):
    """Persist cart dict to session."""
    request.session[CART_SESSION_KEY] = {k: int(v) for k, v in cart.items() if int(v) > 0}
    request.session.modified = True


def cart_to_items_data(cart):
    """Convert session cart to list of { product_id, quantity } for order creation."""
    return [{'product': int(pid), 'quantity': int(qty)} for pid, qty in cart.items() if int(qty) > 0]


def compute_subtotal_and_validate_stock(items_data):
    """
    Validate stock and compute subtotal with current prices (server-side only).
    Returns (validated_items, subtotal). Raises ValidationError on stock/price issues.
    """
    from rest_framework import serializers
    validated = []
    subtotal = Decimal('0.00')
    for item in items_data:
        product = Product.objects.select_for_update().get(pk=item['product'])
        qty = item['quantity']
        if not product.allow_backorder and product.stock_quantity < qty:
            raise serializers.ValidationError({
                'cart': f'Insufficient stock for "{product.name_en}". Available: {product.stock_quantity}.'
            })
        unit_price = product.discount_price if (
            product.discount_price is not None and product.discount_price < product.price
        ) else product.price
        total = unit_price * qty
        subtotal += total
        validated.append({
            'product': product,
            'quantity': qty,
            'unit_price_at_purchase': unit_price,
            'total': total,
            'product_snapshot': {
                'name_en': product.name_en,
                'name_ar': product.name_ar or '',
                'sku': product.sku or '',
            },
        })
    return validated, subtotal


def apply_coupon_to_subtotal(code, subtotal):
    """Validate coupon and return (coupon, discount_amount). Raises ValidationError if invalid."""
    from rest_framework import serializers
    if not code:
        return None, Decimal('0.00')
    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        raise serializers.ValidationError({'coupon_code': 'Invalid coupon code.'})
    if not coupon.is_active:
        raise serializers.ValidationError({'coupon_code': 'This coupon is not active.'})
    now = timezone.now()
    if coupon.valid_from and now < coupon.valid_from:
        raise serializers.ValidationError({'coupon_code': 'This coupon is not yet valid.'})
    if coupon.valid_until and now > coupon.valid_until:
        raise serializers.ValidationError({'coupon_code': 'This coupon has expired.'})
    if coupon.max_uses is not None and coupon.uses_count >= coupon.max_uses:
        raise serializers.ValidationError({'coupon_code': 'This coupon has reached its maximum uses.'})
    if subtotal < coupon.min_order_total:
        raise serializers.ValidationError({
            'coupon_code': f'Minimum order total for this coupon is {coupon.min_order_total}.'
        })
    if coupon.discount_type == 'percent':
        discount = (subtotal * coupon.discount_value / 100).quantize(Decimal('0.01'))
    else:
        discount = min(coupon.discount_value, subtotal)
    return coupon, discount


def compute_tax(subtotal_after_discount: Decimal) -> Decimal:
    """Tax from settings (CHECKOUT_TAX_RATE). Applied to subtotal after discount."""
    rate = getattr(settings, 'CHECKOUT_TAX_RATE', 0) or 0
    return (subtotal_after_discount * Decimal(str(rate))).quantize(Decimal('0.01'))


def compute_shipping() -> Decimal:
    """Shipping from settings (CHECKOUT_SHIPPING_FIXED)."""
    fixed = getattr(settings, 'CHECKOUT_SHIPPING_FIXED', 0) or 0
    return Decimal(str(fixed)).quantize(Decimal('0.01'))


@transaction.atomic
def checkout_create_order_and_payment(request, validated_customer, provider='stripe'):
    """
    Checkout: validate cart (stock, price, coupon), calculate totals (subtotal, discount, tax, shipping),
    create Order and OrderItems in one transaction. Does NOT deduct stock — stock is deducted
    in webhook when payment is confirmed. Creates Payment and optionally Stripe PaymentIntent.
    Returns (order, payment, payment_client_secret, payment_url).
    """
    from rest_framework import serializers
    from .payment_providers import get_stripe_client_secret, get_paypal_payment_url

    cart = get_cart(request)
    if not cart:
        raise serializers.ValidationError({'cart': 'Cart is empty.'})
    items_data = cart_to_items_data(cart)
    # Lock products for update to prevent overselling between checkout and webhook
    validated_items, subtotal = compute_subtotal_and_validate_stock(items_data)
    coupon_code = validated_customer.get('coupon_code', '').strip()
    coupon, discount_amount = apply_coupon_to_subtotal(coupon_code, subtotal)
    subtotal_after_discount = subtotal - discount_amount
    tax_amount = compute_tax(subtotal_after_discount)
    shipping_amount = compute_shipping()
    total = (subtotal_after_discount + tax_amount + shipping_amount).quantize(Decimal('0.01'))

    user = getattr(request, 'user', None) if request else None
    if user and user.is_authenticated:
        customer_email = validated_customer.get('customer_email') or user.email
    else:
        customer_email = validated_customer.get('customer_email', '')

    delivery_address = validated_customer.get('delivery_address')
    shipping_line1 = shipping_line2 = shipping_city = shipping_region = shipping_postal = shipping_country = ''
    if delivery_address:
        shipping_line1 = delivery_address.line1
        shipping_line2 = delivery_address.line2 or ''
        shipping_city = delivery_address.city
        shipping_region = delivery_address.state_region or ''
        shipping_postal = delivery_address.postal_code or ''
        shipping_country = delivery_address.country or 'IL'

    order = Order.objects.create(
        public_id='ord_' + uuid.uuid4().hex[:12],
        user=user if (user and user.is_authenticated) else None,
        customer_name=validated_customer['customer_name'],
        customer_phone=validated_customer['customer_phone'],
        customer_email=customer_email,
        delivery_address=delivery_address,
        shipping_line1=shipping_line1,
        shipping_line2=shipping_line2,
        shipping_city=shipping_city,
        shipping_region=shipping_region,
        shipping_postal=shipping_postal,
        shipping_country=shipping_country,
        notes=validated_customer.get('notes', ''),
        subtotal=subtotal,
        discount_amount=discount_amount,
        tax_amount=tax_amount,
        shipping_amount=shipping_amount,
        total=total,
        currency='ILS',
        coupon=coupon,
        status='pending',
    )
    for item in validated_items:
        OrderItem.objects.create(
            order=order,
            product=item['product'],
            product_snapshot=item['product_snapshot'],
            quantity=item['quantity'],
            unit_price_at_purchase=item['unit_price_at_purchase'],
            total=item['total'],
        )
    # Do NOT deduct stock here — only after webhook confirms payment (prevents oversell if user abandons)
    if coupon:
        coupon.uses_count += 1
        coupon.save(update_fields=['uses_count', 'updated_at'])

    payment = Payment.objects.create(
        order=order,
        provider=provider,
        status='pending',
        amount=total,
        currency='ILS',
    )

    payment_client_secret = None
    payment_url = None
    if provider == 'stripe':
        try:
            payment_client_secret, external_id = get_stripe_client_secret(
                total, order.currency, payment.id, order.public_id
            )
            if external_id:
                payment.external_id = external_id
                payment.save(update_fields=['external_id'])
        except Exception as e:
            logger.exception("Checkout: Stripe PaymentIntent failed for order %s: %s", order.public_id, e)
            raise serializers.ValidationError({'payment': 'Payment provider error. Please try again.'})
    elif provider == 'paypal':
        payment_url = get_paypal_payment_url(
            total, order.currency, payment.id, order.public_id,
            return_url=validated_customer.get('return_url', ''),
            cancel_url=validated_customer.get('cancel_url', ''),
        )

    return order, payment, payment_client_secret, payment_url


def handle_payment_webhook_stripe(raw_body: bytes, signature_header: str):
    """
    Verify Stripe webhook signature, then in one transaction:
    - If payment_intent.succeeded: mark Payment captured, Order paid, deduct stock, create InventoryLog.
    - Idempotency: if Payment already captured (or Order already paid), skip deduction and return (payment, order).
    Returns (payment, order) or (None, None) if event not handled. Raises on signature failure.
    """
    from .payment_providers import verify_stripe_webhook

    event = verify_stripe_webhook(raw_body, signature_header)
    # Support both dict and Stripe Object
    event_type = getattr(event, 'type', None) or (event.get('type') if isinstance(event, dict) else None)
    if event_type != 'payment_intent.succeeded':
        logger.info("Webhook ignored: type=%s", event_type)
        return None, None

    data = getattr(event, 'data', None) or event.get('data', {})
    obj = getattr(data, 'object', None) if data is not None else (data.get('object') if isinstance(data, dict) else None)
    if obj is None and isinstance(data, dict):
        obj = data.get('object', {})
    payment_intent = obj or {}
    external_id = getattr(payment_intent, 'id', None) or (payment_intent.get('id') if isinstance(payment_intent, dict) else None)
    if not external_id:
        logger.warning("Webhook: payment_intent missing id")
        return None, None

    payment = Payment.objects.select_related('order').filter(
        provider='stripe', external_id=external_id
    ).first()
    if not payment:
        logger.warning("Webhook: no Payment for external_id=%s", external_id)
        return None, None

    # Idempotency: already processed — do not deduct stock again
    if payment.status == 'captured':
        logger.info("Webhook: idempotent skip, payment %s already captured", payment.id)
        return payment, payment.order
    if payment.order.status == 'paid':
        payment.status = 'captured'
        payment.save(update_fields=['status', 'updated_at'])
        return payment, payment.order

    with transaction.atomic():
        # Re-fetch with lock to avoid double processing under concurrency
        payment = Payment.objects.select_for_update().select_related('order').get(pk=payment.id)
        if payment.status == 'captured':
            return payment, payment.order
        order = payment.order
        order_items = list(order.items.select_related('product').all())
        # Deduct stock and create InventoryLog for each item
        user = None
        for item in order_items:
            if not item.product_id:
                continue
            product = Product.objects.select_for_update().get(pk=item.product_id)
            if not product.allow_backorder and product.stock_quantity < item.quantity:
                raise ValueError(f'Insufficient stock for product {product.name_en} (order already placed).')
            log_stock_change(
                product,
                -item.quantity,
                reason='sale',
                reference_type='order',
                reference_id=order.id,
                notes=f'Order {order.public_id} (payment confirmed)',
                user=user,
            )
        payment.status = 'captured'
        payment.webhook_verified = True
        # Store minimal audit dict (Stripe event may not be JSON-serializable)
        event_id = getattr(event, 'id', None) or (event.get('id') if isinstance(event, dict) else None)
        payment.webhook_payload = {
            'id': event_id, 'type': event_type,
            'payment_intent_id': external_id,
        }
        payment.webhook_received_at = timezone.now()
        payment.save(update_fields=['status', 'webhook_verified', 'webhook_payload', 'webhook_received_at', 'updated_at'])
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save(update_fields=['status', 'paid_at', 'updated_at'])
        logger.info("Webhook: order %s marked paid, stock deducted", order.public_id)
    return payment, order
