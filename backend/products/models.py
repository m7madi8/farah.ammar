"""
Products app: Category, Product, ProductImage, ProductCategory (M2M), InventoryLog.
Aligns with ER: slug/SKU unique, DecimalField for prices, timestamps.
"""
from django.db import models
from django.conf import settings


class Category(models.Model):
    """Product categories; slug used in frontend filters."""
    slug = models.SlugField(max_length=100, unique=True)
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'slug']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='products_category_slug_unique'),
        ]

    def __str__(self):
        return self.name_en


class Product(models.Model):
    """
    Core product: price, stock, i18n names. order_items store price at purchase.
    """
    slug = models.SlugField(max_length=200, unique=True)
    sku = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True)
    description_en = models.TextField(blank=True)
    description_ar = models.TextField(blank=True)
    badge = models.CharField(max_length=50, blank=True)  # Signature, Sauce, etc.
    # discount_price: optional sale price; if set, frontend may show both
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Optional sale price.',
    )
    currency = models.CharField(max_length=3, default='ILS')
    cost_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    stock_quantity = models.IntegerField(default=0)
    allow_backorder = models.BooleanField(default=False)
    weight = models.DecimalField(
        max_digits=10, decimal_places=3, null=True, blank=True,
        help_text='Weight in kg (optional).',
    )
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    categories = models.ManyToManyField(
        'Category',
        through='ProductCategory',
        related_name='products',
        blank=True,
    )

    class Meta:
        ordering = ['sort_order', 'slug']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        constraints = [
            models.UniqueConstraint(fields=['slug'], name='products_product_slug_unique'),
            models.UniqueConstraint(fields=['sku'], condition=models.Q(sku__isnull=False), name='products_product_sku_unique'),
            models.CheckConstraint(check=models.Q(price__gte=0), name='products_product_price_non_neg'),
            models.CheckConstraint(check=models.Q(stock_quantity__gte=0), name='products_product_stock_non_neg'),
        ]

    def __str__(self):
        return self.name_en


class ProductCategory(models.Model):
    """Through model: product–category M2M with is_primary flag. One primary per product."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_category_links')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product_links')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['product', 'category']]
        verbose_name = 'Product category'
        verbose_name_plural = 'Product categories'
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_primary=True),
                name='products_productcategory_one_primary',
            ),
        ]

    def __str__(self):
        return f"{self.product.name_en} — {self.category.name_en}"


class ProductImage(models.Model):
    """Multiple images per product; is_hero for main product page image."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.CharField(max_length=1024)  # full URL or path
    alt_en = models.CharField(max_length=255, blank=True)
    alt_ar = models.CharField(max_length=255, blank=True)
    sort_order = models.IntegerField(default=0)
    is_hero = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['sort_order', 'id']
        verbose_name = 'Product image'
        verbose_name_plural = 'Product images'

    def __str__(self):
        return f"{self.product.name_en} — image {self.id}"


class InventoryLog(models.Model):
    """
    Stock movement log. Populated by signals when product stock changes.
    reason: sale, restock, adjustment, return, damage, transfer.
    """
    REASON_CHOICES = [
        ('sale', 'Sale'),
        ('restock', 'Restock'),
        ('adjustment', 'Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
        ('transfer', 'Transfer'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    change_qty = models.IntegerField()  # positive = in, negative = out
    quantity_after = models.IntegerField()
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reference_type = models.CharField(max_length=30, blank=True)  # order, manual, purchase_order
    reference_id = models.BigIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_logs',
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Inventory log'
        verbose_name_plural = 'Inventory logs'
        constraints = [
            models.CheckConstraint(check=models.Q(change_qty__gt=0) | models.Q(change_qty__lt=0), name='products_inv_change_nonzero'),
        ]

    def __str__(self):
        return f"{self.product.name_en} {self.change_qty:+d} → {self.quantity_after} ({self.reason})"
