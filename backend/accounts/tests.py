"""Tests for accounts: User model, registration, login, profile."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(email='test@example.com', password='testpass123', full_name='Test User')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'customer')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_email_unique(self):
        User.objects.create_user(email='a@b.com', password='x', full_name='A')
        with self.assertRaises(Exception):
            User.objects.create_user(email='a@b.com', password='y', full_name='B')

    def test_str(self):
        user = User.objects.create_user(email='u@u.com', password='p', full_name='U')
        self.assertIn('u@u.com', str(user))


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_success(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'new@example.com',
            'password': 'securepass123',
            'full_name': 'New User',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', resp.data)
        self.assertIn('user', resp.data)
        self.assertEqual(resp.data['user']['email'], 'new@example.com')
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_register_validation(self):
        resp = self.client.post('/api/auth/register/', {
            'email': 'bad',
            'password': 'short',
            'full_name': '',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(email='login@example.com', password='pass123', full_name='L')
        resp = self.client.post('/api/auth/login/', {
            'email': 'login@example.com',
            'password': 'pass123',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('token', resp.data)

    def test_login_invalid(self):
        resp = self.client.post('/api/auth/login/', {
            'email': 'nonexistent@example.com',
            'password': 'wrong',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_token(self):
        user = User.objects.create_user(email='me@example.com', password='p', full_name='Me')
        self.client.force_authenticate(user=user)
        resp = self.client.get('/api/auth/me/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['email'], 'me@example.com')
