"""
Orders app: Coupon, Order, OrderItem, Payment.
Guest checkout supported (user_id nullable); order_items store unit_price_at_purchase.
"""
from django.db import models
from django.conf import settings


class Coupon(models.Model):
    """Discount codes: percent or fixed; optional validity and max_uses."""
    DISCOUNT_TYPES = [('percent', 'Percent'), ('fixed', 'Fixed')]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.IntegerField(null=True, blank=True)  # NULL = unlimited
    uses_count = models.IntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        constraints = [
            models.UniqueConstraint(fields=['code'], name='orders_coupon_code_unique'),
            models.CheckConstraint(check=models.Q(discount_value__gt=0), name='orders_coupon_value_positive'),
        ]

    def __str__(self):
        return self.code


class Order(models.Model):
    """
    Order header. Guest orders: user_id NULL, customer_* and shipping_* from form.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    public_id = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    customer_email = models.EmailField(blank=True)
    delivery_address = models.ForeignKey(
        'accounts.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    # Snapshot of address at order time
    shipping_line1 = models.CharField(max_length=255, blank=True)
    shipping_line2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_region = models.CharField(max_length=100, blank=True)
    shipping_postal = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=2, blank=True)
    notes = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='ILS')
    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
    )
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        constraints = [
            models.UniqueConstraint(fields=['public_id'], name='orders_order_public_id_unique'),
            models.CheckConstraint(check=models.Q(total__gte=0), name='orders_order_total_non_neg'),
        ]

    def __str__(self):
        return f"Order {self.public_id}"


class OrderItem(models.Model):
    """Line item: product snapshot and unit_price at purchase time."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    product_snapshot = models.JSONField(default=dict, blank=True)  # { name_en, name_ar, sku }
    quantity = models.PositiveIntegerField()
    unit_price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['id']
        verbose_name = 'Order item'
        verbose_name_plural = 'Order items'
        constraints = [
            models.CheckConstraint(check=models.Q(unit_price_at_purchase__gte=0), name='orders_orderitem_price_non_neg'),
        ]

    def __str__(self):
        return f"{self.order.public_id} — {self.quantity}x"


class Payment(models.Model):
    """Payment per order; multiple providers supported."""
    PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('cod', 'Cash on Delivery'),
        ('bank_transfer', 'Bank Transfer'),
        ('other', 'Other'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('captured', 'Captured'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=30, choices=PROVIDER_CHOICES)
    external_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='ILS')
    metadata = models.JSONField(default=dict, blank=True)
    webhook_verified = models.BooleanField(default=False)
    webhook_payload = models.JSONField(null=True, blank=True)
    webhook_received_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f"{self.order.public_id} — {self.provider} ({self.status})"
