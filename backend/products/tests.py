"""Tests for products: Category, Product models, API list/detail."""
from decimal import Decimal
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Category, Product, ProductImage, ProductCategory


class CategoryModelTest(TestCase):
    def test_str(self):
        c = Category.objects.create(slug='boxes', name_en='Boxes')
        self.assertIn('Boxes', str(c))

    def test_slug_unique(self):
        Category.objects.create(slug='x', name_en='X')
        with self.assertRaises(Exception):
            Category.objects.create(slug='x', name_en='Y')


class ProductModelTest(TestCase):
    def setUp(self):
        self.cat = Category.objects.create(slug='sauces', name_en='Sauces')

    def test_create_product(self):
        p = Product.objects.create(
            slug='teriyaki',
            name_en='Teriyaki',
            price=Decimal('10.00'),
            stock_quantity=5,
        )
        self.assertEqual(p.price, Decimal('10.00'))
        self.assertEqual(p.stock_quantity, 5)

    def test_slug_unique(self):
        Product.objects.create(slug='x', name_en='X', price=Decimal('1'))
        with self.assertRaises(Exception):
            Product.objects.create(slug='x', name_en='Y', price=Decimal('1'))


class ProductAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.product = Product.objects.create(
            slug='test-product',
            name_en='Test Product',
            price=Decimal('25.00'),
            stock_quantity=10,
            is_active=True,
        )

    def test_list_products(self):
        resp = self.client.get('/api/products/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        self.assertGreaterEqual(len(resp.data['results']), 1)

    def test_product_detail(self):
        resp = self.client.get(f'/api/products/{self.product.slug}/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['slug'], 'test-product')
        self.assertEqual(resp.data['name_en'], 'Test Product')
        self.assertIn('images', resp.data)
        self.assertIn('categories', resp.data)

    def test_product_detail_404(self):
        resp = self.client.get('/api/products/nonexistent-slug/')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
