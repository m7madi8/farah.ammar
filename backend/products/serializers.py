"""
Product serializers: nested images and categories for React frontend.
InventoryLogSerializer is read-only.
"""
from rest_framework import serializers
from .models import Category, Product, ProductImage, ProductCategory, InventoryLog


class CategorySerializer(serializers.ModelSerializer):
    """Category list/detail for nesting in product payloads."""

    class Meta:
        model = Category
        fields = ('id', 'slug', 'name_en', 'name_ar', 'description', 'sort_order', 'is_active')
        read_only_fields = fields


class ProductImageSerializer(serializers.ModelSerializer):
    """Nested product image; url can be full URL or path."""

    class Meta:
        model = ProductImage
        fields = ('id', 'url', 'alt_en', 'alt_ar', 'sort_order', 'is_hero', 'created_at')
        read_only_fields = ('id', 'created_at')


class ProductCategoryLinkSerializer(serializers.ModelSerializer):
    """Through model representation: category + is_primary."""
    category = CategorySerializer(read_only=True)

    class Meta:
        model = ProductCategory
        fields = ('id', 'category', 'is_primary', 'created_at')
        read_only_fields = fields


class ProductSerializer(serializers.ModelSerializer):
    """
    Product with nested images and categories for frontend.
    Price validation: price and discount_price >= 0; discount_price < price if set.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    categories = ProductCategoryLinkSerializer(source='product_category_links', many=True, read_only=True)

    class Meta:
        model = Product
        fields = (
            'id', 'slug', 'sku', 'name_en', 'name_ar',
            'description_en', 'description_ar', 'badge',
            'price', 'discount_price', 'currency', 'cost_price',
            'stock_quantity', 'allow_backorder', 'weight',
            'sort_order', 'is_active',
            'created_at', 'updated_at',
            'images', 'categories',
        )
        read_only_fields = (
            'id', 'slug', 'created_at', 'updated_at',
            'images', 'categories',
        )

    def validate(self, data):
        price = data.get('price', getattr(self.instance, 'price', None))
        discount_price = data.get('discount_price', getattr(self.instance, 'discount_price', None))
        if price is not None and price < 0:
            raise serializers.ValidationError({'price': 'Price must be >= 0.'})
        if discount_price is not None:
            if discount_price < 0:
                raise serializers.ValidationError({'discount_price': 'Discount price must be >= 0.'})
            if price is not None and discount_price >= price:
                raise serializers.ValidationError({'discount_price': 'Discount price must be less than price.'})
        return data


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight product list (e.g. for catalog); optional hero image and primary category slug for filtering."""
    hero_image = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id', 'slug', 'name_en', 'name_ar', 'price', 'discount_price',
            'currency', 'stock_quantity', 'is_active', 'hero_image', 'category',
        )

    def get_hero_image(self, obj):
        hero = obj.images.filter(is_hero=True).first()
        return ProductImageSerializer(hero).data if hero else None

    def get_category(self, obj):
        link = obj.product_category_links.order_by('-is_primary').first()
        return link.category.slug if link else None


class InventoryLogSerializer(serializers.ModelSerializer):
    """Read-only inventory log for auditing and admin/API display."""

    class Meta:
        model = InventoryLog
        fields = (
            'id', 'product', 'change_qty', 'quantity_after', 'reason',
            'reference_type', 'reference_id', 'notes',
            'created_at', 'created_by',
        )
        read_only_fields = fields
