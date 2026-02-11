"""
Accounts app: Custom User and Address models for Chef Farah Ammar.
User uses email as USERNAME_FIELD; role customer/admin; optional soft delete.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for email-based User model."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'super_admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('role') != 'super_admin':
            raise ValueError('Superuser must have role=super_admin.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user with email as username.
    role: customer | admin | super_admin.
    Optional soft delete: is_active=False (Django standard).
    """
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]
    LANG_CHOICES = [('en', 'English'), ('ar', 'Arabic')]

    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50, blank=True)
    preferred_lang = models.CharField(max_length=2, choices=LANG_CHOICES, default='en')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)  # type: ignore[reportArgumentType]
    is_staff = models.BooleanField(default=False)  # type: ignore[reportArgumentType]
    email_verified_at = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:  # type: ignore[reportIncompatibleVariableOverride]
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(fields=['email'], name='accounts_user_email_unique'),
        ]

    def __str__(self) -> str:
        return str(self.email)


class Address(models.Model):
    """
    Delivery/billing address. user_id can be NULL for guest one-off addresses.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='addresses',
    )
    label = models.CharField(max_length=100, blank=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state_region = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=2, default='IL')
    is_default = models.BooleanField(default=False)  # type: ignore[reportArgumentType]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.full_name} — {self.line1}, {self.city}"
