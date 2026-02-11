"""
Chef Farah Ammar — URL configuration.
API under /api/: auth, products, orders (incl. cart, checkout, webhook, coupon).
Admin: custom dashboard at /admin/ (admin/super_admin only).
"""
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from config.admin import admin_site

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin_site.urls),
    path('api/auth/', include('accounts.urls', namespace='accounts')),
    path('api/', include('products.urls', namespace='products')),
    path('api/', include('orders.urls', namespace='orders')),
]

# خدمة الملفات الثابتة (CSS/JS) في وضع التطوير — يمنع خطأ MIME type
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
