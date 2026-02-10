from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address  # نفس موديلاتك

# UserAdmin
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('full_name', 'phone', 'preferred_lang')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'email_verified_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'password1', 'password2', 'full_name', 'phone',
                'preferred_lang', 'role', 'is_active', 'is_staff'
            )
        }),
    )

# AddressAdmin
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'line1', 'city', 'country', 'user', 'is_default', 'created_at')
    list_filter = ('country', 'is_default')
    search_fields = ('full_name', 'line1', 'city')
    ordering = ('-is_default', '-created_at')
