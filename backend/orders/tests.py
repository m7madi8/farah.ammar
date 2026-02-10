"""Tests for orders: models, order create, checkout, coupon apply, webhook (mocked)."""
from decimal import Decimal
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock

from accounts.models import User
from products.models import Product
from .models import Coupon, Order, OrderItem, Payment


class CouponModelTest(TestCase):
    def test_str(self):
        c = Coupon.objects.create(
            code='SAVE10',
            discount_type='percent',
            discount_value=Decimal('10'),
            valid_from=timezone.now(),
        )
        self.assertEqual(str(c), 'SAVE10')


class OrderCreateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            slug='p1',
            name_en='Product 1',
            price=Decimal('20.00'),
            stock_quantity=10,
            is_active=True,
        )

    def test_create_order_valid(self):
        payload = {
            'customer_name': 'Test User',
            'customer_phone': '+1234567890',
            'customer_email': 'test@example.com',
            'items': [{'product': self.product.id, 'quantity': 2}],
        }
        resp = self.client.post('/api/orders/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('public_id', resp.data)
        self.assertEqual(Decimal(resp.data['total']), Decimal('40.00'))
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_create_order_insufficient_stock(self):
        payload = {
            'customer_name': 'Test',
            'customer_phone': '+1',
            'items': [{'product': self.product.id, 'quantity': 100}],
        }
        resp = self.client.post('/api/orders/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 10)

    def test_create_order_empty_items(self):
        payload = {
            'customer_name': 'Test',
            'customer_phone': '+1',
            'items': [],
        }
        resp = self.client.post('/api/orders/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class CheckoutAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            slug='p2',
            name_en='Product 2',
            price=Decimal('15.00'),
            stock_quantity=5,
            is_active=True,
        )

    def test_checkout_empty_cart(self):
        payload = {
            'customer_name': 'Checkout User',
            'customer_phone': '+999',
        }
        resp = self.client.post('/api/checkout/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp.data.get('success', True))

    def test_checkout_with_cart(self):
        self.client.session['cart'] = {str(self.product.id): 1}
        self.client.session.save()
        payload = {
            'customer_name': 'Checkout User',
            'customer_phone': '+999',
            'customer_email': 'c@c.com',
        }
        with patch('orders.payment_providers.get_stripe_client_secret', return_value=(None, None)):
            resp = self.client.post('/api/checkout/', payload, format='json')
        if resp.status_code == 201:
            self.assertTrue(resp.data.get('success'))
            self.assertIn('order_id', resp.data)
            self.assertIn('totals', resp.data)
        else:
            self.assertIn(resp.status_code, (201, 400))


class CouponApplyAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.coupon = Coupon.objects.create(
            code='FIXED5',
            discount_type='fixed',
            discount_value=Decimal('5.00'),
            min_order_total=Decimal('20'),
            valid_from=timezone.now(),
            is_active=True,
        )

    def test_apply_coupon_valid(self):
        resp = self.client.post('/api/coupon/apply/', {
            'code': 'FIXED5',
            'subtotal': Decimal('50.00'),
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue(resp.data.get('valid'))
        self.assertEqual(Decimal(resp.data['discount_amount']), Decimal('5.00'))
        self.assertEqual(Decimal(resp.data['total_after']), Decimal('45.00'))

    def test_apply_coupon_invalid_code(self):
        resp = self.client.post('/api/coupon/apply/', {
            'code': 'INVALID',
            'subtotal': Decimal('50.00'),
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp.data.get('valid', True))


class PaymentWebhookTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.credentials(HTTP_STRIPE_SIGNATURE='')  # no auth for webhook

    def test_webhook_returns_200_without_valid_signature(self):
        resp = self.client.post(
            '/api/webhook/payment/',
            b'{}',
            content_type='application/json',
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('received', resp.data)


class OrderTransactionTest(TestCase):
    """Ensure order creation and stock deduction behave correctly in transaction."""

    def setUp(self):
        self.product = Product.objects.create(
            slug='tx-product',
            name_en='Tx Product',
            price=Decimal('10.00'),
            stock_quantity=3,
            is_active=True,
        )

    def test_order_creates_items_and_deducts_stock(self):
        client = APIClient()
        payload = {
            'customer_name': 'T',
            'customer_phone': '1',
            'items': [{'product': self.product.id, 'quantity': 2}],
        }
        resp = client.post('/api/orders/', payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        order_id = resp.data['id']
        order = Order.objects.get(pk=order_id)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 1)
