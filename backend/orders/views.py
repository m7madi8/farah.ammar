"""
Orders API: list (admin only), retrieve, create, status update (admin),
cart (add/remove/get), checkout, payment webhook, coupon apply.
Class-based views; permissions and validation applied.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from config.permissions import IsAdminRole
from .models import Order, OrderItem, Coupon, Payment
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
    CouponSerializer,
    CartAddSerializer,
    CartRemoveSerializer,
    CheckoutSerializer,
    CouponApplySerializer,
)
from .services import (
    get_cart,
    set_cart,
    get_cart_response,
    checkout_create_order_and_payment,
    handle_payment_webhook_stripe,
    apply_coupon_to_subtotal,
)
from products.models import Product


# ---------- Order ViewSet ----------
class OrderViewSet(viewsets.ModelViewSet):
    """
    Orders: list (admin only), retrieve (owner or admin or guest by public_id),
    create (any), update_status (admin only).
    """
    serializer_class = OrderSerializer
    lookup_field = 'public_id'
    lookup_value_regex = '[a-zA-Z0-9_]+'

    def get_permissions(self):
        if self.action == 'list':
            return [IsAdminRole()]
        if self.action == 'update_status':
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        qs = Order.objects.prefetch_related('items', 'payments').select_related(
            'delivery_address', 'coupon', 'user',
        )
        if self.request.user.is_authenticated:
            if getattr(self.request.user, 'role', None) in ('admin', 'super_admin'):
                return qs
            return qs.filter(user=self.request.user)
        if self.action == 'retrieve':
            return qs
        return qs.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        if self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'], url_path='status')
    def update_status(self, request, public_id=None):
        """PATCH /api/orders/:public_id/status/ — Update order status (admin only)."""
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)


# ---------- Coupon ViewSet (read-only) ----------
class CouponViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/coupons/ and GET /api/coupons/:code/ — List and retrieve coupons."""
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    lookup_field = 'code'


# ---------- Cart (session-based) ----------
class CartAddView(APIView):
    """POST /api/cart/add/ — Add product to cart (product id, quantity)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        cart = get_cart(request)
        pid = str(product.id)
        cart[pid] = cart.get(pid, 0) + quantity
        set_cart(request, cart)
        return Response(get_cart_response(request), status=status.HTTP_200_OK)


class CartRemoveView(APIView):
    """POST /api/cart/remove/ — Remove product from cart (product id, optional quantity)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CartRemoveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data.get('quantity')
        cart = get_cart(request)
        pid = str(product.id)
        if pid not in cart:
            return Response({'detail': 'Product not in cart.'}, status=status.HTTP_400_BAD_REQUEST)
        if quantity is None:
            del cart[pid]
        else:
            cart[pid] = max(0, cart[pid] - quantity)
            if cart[pid] == 0:
                del cart[pid]
        set_cart(request, cart)
        return Response(get_cart_response(request), status=status.HTTP_200_OK)


class CartDetailView(APIView):
    """GET /api/cart/ — Get cart details (items with product info, subtotal)."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(get_cart_response(request))


# ---------- Checkout ----------
class CheckoutView(APIView):
    """
    POST /api/checkout/ — Validate cart (stock, price, coupon), calculate totals,
    create Order and OrderItems in a transaction. Return payment_client_secret (Stripe)
    or payment_url (PayPal). Stock is NOT deducted here; deducted in webhook after payment.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # 1. Validate input; return unified error JSON for React
        import logging
        logger = logging.getLogger(__name__)
        serializer = CheckoutSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # 2. Create order in transaction (stock validated but not deducted until webhook)
        try:
            provider = serializer.validated_data.get('payment_provider', 'stripe')
            order, payment, payment_client_secret, payment_url = checkout_create_order_and_payment(
                request, serializer.validated_data, provider=provider
            )
        except Exception as e:
            from rest_framework.exceptions import ValidationError
            logger.exception("Checkout failed: %s", e)
            if isinstance(e, ValidationError):
                return Response({
                    'success': False,
                    'errors': e.detail,
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'success': False,
                'errors': {'detail': str(e)},
            }, status=status.HTTP_400_BAD_REQUEST)
        set_cart(request, {})
        order_serializer = OrderSerializer(order)
        # 3. Structured JSON for React: success, order_id, payment_client_secret / payment_url
        return Response({
            'success': True,
            'order_id': order.id,
            'order_public_id': order.public_id,
            'order': order_serializer.data,
            'totals': {
                'subtotal': str(order.subtotal),
                'discount': str(order.discount_amount),
                'tax': str(order.tax_amount),
                'shipping': str(order.shipping_amount),
                'total': str(order.total),
            },
            'payment_client_secret': payment_client_secret,
            'payment_url': payment_url,
        }, status=status.HTTP_201_CREATED)


# ---------- Payment webhook ----------
@method_decorator(csrf_exempt, name='dispatch')
class PaymentWebhookView(APIView):
    """
    POST /api/webhook/payment/ — Stripe (and optionally PayPal) webhook.
    Verify provider signature; on payment success update Order (paid), deduct stock,
    create InventoryLog in one transaction. Idempotent: 200 OK always; no double deduction.
    """
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        import logging
        logger = logging.getLogger(__name__)
        # Stripe requires raw body for signature verification — do not use request.data
        raw_body = request.body
        sig = request.META.get('HTTP_STRIPE_SIGNATURE') or request.META.get('HTTP_X_STRIPE_SIGNATURE') or ''
        try:
            payment, order = handle_payment_webhook_stripe(raw_body, sig)
        except ValueError as e:
            logger.warning("Webhook signature or validation failed: %s", e)
            # Return 200 so provider does not retry
            return Response({'received': True}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.exception("Webhook processing failed: %s", e)
            return Response({'received': True}, status=status.HTTP_200_OK)
        if payment and order:
            return Response({'received': True, 'order_public_id': order.public_id}, status=status.HTTP_200_OK)
        return Response({'received': True}, status=status.HTTP_200_OK)


# ---------- Coupon apply ----------
class CouponApplyView(APIView):
    """POST /api/coupon/apply/ — Validate coupon and return discount for given subtotal."""
    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework.exceptions import ValidationError
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['code'].strip()
        subtotal = serializer.validated_data['subtotal']
        try:
            coupon, discount_amount = apply_coupon_to_subtotal(code, subtotal)
        except ValidationError as e:
            return Response({'valid': False, 'errors': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        total_after = subtotal - discount_amount
        return Response({
            'valid': True,
            'code': coupon.code if coupon else None,
            'discount_amount': str(discount_amount),
            'subtotal': str(subtotal),
            'total_after': str(total_after),
        })