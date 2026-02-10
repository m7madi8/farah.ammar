"""
Order serializers: nested OrderItems, Address, Payment for React.
Stock validation, server-side price validation, coupon validation (active, max_uses, expiry).
"""
from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone

from accounts.serializers import AddressSerializer
from accounts.models import Address
from products.models import Product
from products.signals import log_stock_change

from .models import Coupon, Order, OrderItem, Payment


# ---------- Coupon ----------
class CouponSerializer(serializers.ModelSerializer):
    """
    Coupon for display and validation.
    Validate: is_active, valid_from <= now <= valid_until (if set), uses_count < max_uses.
    """

    class Meta:
        model = Coupon
        fields = (
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'min_order_total', 'max_uses', 'uses_count', 'valid_from', 'valid_until',
            'is_active', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'uses_count', 'created_at', 'updated_at',
        )

    def validate_code_active(self, code):
        """Validate coupon by code: active, within validity, and under max_uses."""
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return None
        if not coupon.is_active:
            raise serializers.ValidationError({'coupon': 'This coupon is not active.'})
        now = timezone.now()
        if coupon.valid_from and now < coupon.valid_from:
            raise serializers.ValidationError({'coupon': 'This coupon is not yet valid.'})
        if coupon.valid_until and now > coupon.valid_until:
            raise serializers.ValidationError({'coupon': 'This coupon has expired.'})
        if coupon.max_uses is not None and coupon.uses_count >= coupon.max_uses:
            raise serializers.ValidationError({'coupon': 'This coupon has reached its maximum uses.'})
        return coupon


# ---------- Order items & payment (nested) ----------
class OrderItemSerializer(serializers.ModelSerializer):
    """Single line item; product snapshot and unit_price_at_purchase (read-only after create)."""

    class Meta:
        model = OrderItem
        fields = (
            'id', 'product', 'product_snapshot', 'quantity',
            'unit_price_at_purchase', 'total',
        )
        read_only_fields = ('id', 'product_snapshot', 'unit_price_at_purchase', 'total')

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be at least 1.')
        return value


class PaymentSerializer(serializers.ModelSerializer):
    """Read-only payment display in order payload."""

    class Meta:
        model = Payment
        fields = (
            'id', 'order', 'provider', 'external_id', 'status', 'amount', 'currency',
            'metadata', 'webhook_verified', 'created_at', 'updated_at',
        )
        read_only_fields = fields


# ---------- Order ----------
class OrderSerializer(serializers.ModelSerializer):
    """
    Order with nested items, delivery address snapshot, and payments.
    On create: validate stock, server-side prices, coupon (active, max_uses, expiry).
    """
    items = OrderItemSerializer(many=True)
    delivery_address_detail = AddressSerializer(source='delivery_address', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'public_id', 'user', 'customer_name', 'customer_phone', 'customer_email',
            'delivery_address', 'delivery_address_detail',
            'shipping_line1', 'shipping_line2', 'shipping_city', 'shipping_region',
            'shipping_postal', 'shipping_country', 'notes',
            'subtotal', 'discount_amount', 'tax_amount', 'shipping_amount', 'total', 'currency', 'coupon',
            'status', 'paid_at', 'fulfilled_at',
            'created_at', 'updated_at',
            'items', 'payments',
        )
        read_only_fields = (
            'id', 'public_id', 'user', 'subtotal', 'discount_amount', 'tax_amount', 'shipping_amount', 'total',
            'status', 'paid_at', 'fulfilled_at', 'created_at', 'updated_at',
            'delivery_address_detail', 'payments',
        )

    def _validate_stock(self, items_data, request_user=None):
        """Ensure each product has enough stock (or allow_backorder)."""
        for item in items_data:
            product_id = item.get('product')
            if not product_id:
                raise serializers.ValidationError({'items': 'Each item must specify a product.'})
            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError({'items': f'Product id {product_id} not found.'})
            qty = item.get('quantity', 0)
            if qty < 1:
                raise serializers.ValidationError({'items': 'Quantity must be at least 1.'})
            if not product.allow_backorder and product.stock_quantity < qty:
                raise serializers.ValidationError({
                    'items': f'Insufficient stock for product "{product.name_en}". Available: {product.stock_quantity}.'
                })

    def _validate_prices(self, items_data):
        """Server-side: use current product price (or discount_price) for each item."""
        validated_items = []
        subtotal = Decimal('0.00')
        for item in items_data:
            product = Product.objects.get(pk=item['product'])
            qty = item['quantity']
            # Use discount_price if set and less than price
            unit_price = product.discount_price if (
                product.discount_price is not None and product.discount_price < product.price
            ) else product.price
            total = unit_price * qty
            subtotal += total
            validated_items.append({
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
        return validated_items, subtotal

    def _apply_coupon(self, code, subtotal):
        """Validate coupon and return (coupon, discount_amount)."""
        if not code:
            return None, Decimal('0.00')
        serializer = CouponSerializer()
        coupon = serializer.validate_code_active(code)
        if coupon is None:
            raise serializers.ValidationError({'coupon': 'Invalid coupon code.'})
        if subtotal < coupon.min_order_total:
            raise serializers.ValidationError({
                'coupon': f'Minimum order total for this coupon is {coupon.min_order_total}.'
            })
        if coupon.discount_type == 'percent':
            discount = (subtotal * coupon.discount_value / 100).quantize(Decimal('0.01'))
        else:
            discount = min(coupon.discount_value, subtotal)
        return coupon, discount

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        coupon_code = validated_data.pop('coupon_code', None)
        if not coupon_code and validated_data.get('coupon'):
            coupon_code = validated_data['coupon'].code
        request = self.context.get('request')
        request_user = getattr(request, 'user', None) if request else None

        self._validate_stock(items_data, request_user)
        validated_items, subtotal = self._validate_prices(items_data)
        coupon, discount_amount = self._apply_coupon(coupon_code, subtotal)
        total = subtotal - discount_amount

        # Build shipping snapshot from delivery_address if provided
        delivery_address = validated_data.get('delivery_address')
        if delivery_address:
            validated_data['shipping_line1'] = delivery_address.line1
            validated_data['shipping_line2'] = delivery_address.line2 or ''
            validated_data['shipping_city'] = delivery_address.city
            validated_data['shipping_region'] = delivery_address.state_region or ''
            validated_data['shipping_postal'] = delivery_address.postal_code or ''
            validated_data['shipping_country'] = delivery_address.country or 'IL'

        import uuid
        validated_data['public_id'] = 'ord_' + uuid.uuid4().hex[:12]
        validated_data['subtotal'] = subtotal
        validated_data['discount_amount'] = discount_amount
        validated_data['total'] = total
        validated_data['coupon'] = coupon
        # Remove any field not on Order model before create
        validated_data.pop('delivery_address_detail', None)
        if request_user and request_user.is_authenticated:
            validated_data['user'] = request_user
            validated_data.setdefault('customer_email', request_user.email)

        order = Order.objects.create(**validated_data)
        for item in validated_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_snapshot=item['product_snapshot'],
                quantity=item['quantity'],
                unit_price_at_purchase=item['unit_price_at_purchase'],
                total=item['total'],
            )
            # Deduct stock and log
            log_stock_change(
                item['product'],
                -item['quantity'],
                reason='sale',
                reference_type='order',
                reference_id=order.id,
                notes=f'Order {order.public_id}',
                user=request_user,
            )
        if coupon:
            coupon.uses_count += 1
            coupon.save(update_fields=['uses_count', 'updated_at'])
        return order

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('Order must have at least one item.')
        return value


class OrderCreateSerializer(OrderSerializer):
    """Create-only: accept coupon_code and delivery_address id."""
    coupon_code = serializers.CharField(required=False, allow_blank=True, write_only=True)
    delivery_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False, allow_null=True, write_only=True
    )

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ('coupon_code',)
        read_only_fields = [f for f in OrderSerializer.Meta.read_only_fields if f != 'delivery_address']


# ---------- Order status (admin only) ----------
class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """PATCH order status; admin only."""

    class Meta:
        model = Order
        fields = ('status',)

    def validate_status(self, value):
        allowed = [c[0] for c in Order.STATUS_CHOICES]
        if value not in allowed:
            raise serializers.ValidationError(f'Status must be one of: {allowed}.')
        return value


# ---------- Cart (session-based); for checkout request ----------
class CartAddSerializer(serializers.Serializer):
    """POST /api/cart/add/: product id and quantity."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        product = data['product']
        qty = data['quantity']
        if not product.allow_backorder and product.stock_quantity < qty:
            raise serializers.ValidationError({
                'quantity': f'Insufficient stock. Available: {product.stock_quantity}.'
            })
        return data


class CartRemoveSerializer(serializers.Serializer):
    """POST /api/cart/remove/: product id and optional quantity to remove."""
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1, required=False, default=None)


# ---------- Checkout: create order from cart + customer info, return payment intent ----------
class CheckoutSerializer(serializers.Serializer):
    """
    POST /api/checkout/: customer info + optional delivery_address, coupon_code, payment_provider.
    Cart from session; order created in transaction; totals (subtotal, discount, tax, shipping, total).
    """
    customer_name = serializers.CharField(max_length=255)
    customer_phone = serializers.CharField(max_length=50)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    delivery_address = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), required=False, allow_null=True
    )
    coupon_code = serializers.CharField(required=False, allow_blank=True)
    payment_provider = serializers.ChoiceField(
        choices=['stripe', 'paypal'],
        default='stripe',
        required=False,
    )
    return_url = serializers.URLField(required=False, allow_blank=True)
    cancel_url = serializers.URLField(required=False, allow_blank=True)


# ---------- Coupon apply (validate and return discount for given subtotal) ----------
class CouponApplySerializer(serializers.Serializer):
    """POST /api/coupon/apply/: code and subtotal; returns valid, discount_amount, total_after."""
    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=0)
