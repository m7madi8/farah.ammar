from rest_framework import viewsets, filters
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Category, Product, InventoryLog
from .serializers import CategorySerializer, ProductSerializer, ProductListSerializer, InventoryLogSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Categories list and detail (read-only for storefront)."""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['sort_order', 'slug']


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Products list and detail with nested images and categories."""
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        'images', 'product_category_links__category',
    )
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['sort_order', 'price', 'created_at']
    search_fields = ['name_en', 'name_ar', 'sku']

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer


class InventoryLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only inventory logs (e.g. for admin/reports)."""
    queryset = InventoryLog.objects.select_related('product', 'created_by')
    serializer_class = InventoryLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['product', 'reason']
    ordering = ['-created_at']
