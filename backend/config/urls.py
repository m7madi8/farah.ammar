"""
Chef Farah Ammar — URL configuration.
API under /api/: auth, products, orders (incl. cart, checkout, webhook, coupon).
Admin: custom dashboard at /admin/ (admin/super_admin only).
"""
from django.urls import path, include
from config.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    # Auth: register, login, logout, me
    path('api/auth/', include('accounts.urls', namespace='accounts')),
    # Products: list, detail (by slug); categories; inventory-logs
    path('api/', include('products.urls', namespace='products')),
    # Orders: list (admin), retrieve, create, status (admin); cart; checkout; webhook; coupon apply
    path('api/', include('orders.urls', namespace='orders')),
]
