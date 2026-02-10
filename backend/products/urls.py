from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, InventoryLogViewSet

app_name = 'products'

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'inventory-logs', InventoryLogViewSet, basename='inventorylog')

urlpatterns = [
    path('', include(router.urls)),
]
