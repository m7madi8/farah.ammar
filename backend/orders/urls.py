"""Orders API: orders, coupons, cart, checkout, webhook, coupon apply."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrderViewSet,
    CouponViewSet,
    CartAddView,
    CartRemoveView,
    CartDetailView,
    CheckoutView,
    PaymentWebhookView,
    CouponApplyView,
)

app_name = 'orders'

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'coupons', CouponViewSet, basename='coupon')

urlpatterns = [
    path('', include(router.urls)),
    # Cart (session-based)
    path('cart/', CartDetailView.as_view(), name='cart-detail'),
    path('cart/add/', CartAddView.as_view(), name='cart-add'),
    path('cart/remove/', CartRemoveView.as_view(), name='cart-remove'),
    # Checkout & payment
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('webhook/payment/', PaymentWebhookView.as_view(), name='webhook-payment'),
    # Coupon apply (validate code for given subtotal)
    path('coupon/apply/', CouponApplyView.as_view(), name='coupon-apply'),
]
