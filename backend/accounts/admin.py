from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from config.admin import admin_site
from .models import User, Address


@admin_site.register(User)
class UserAdmin(BaseUserAdmin):
    # الحقول اللي تظهر في قائمة المستخدمين
    list_display = ('email', 'full_name', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name')
    ordering = ('-created_at',)

    # ترتيب الحقول داخل صفحة تعديل المستخدم
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profile', {'fields': ('full_name', 'phone', 'preferred_lang')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'email_verified_at')}),
    )

    # صفحة إضافة مستخدم جديد
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'full_name', 'phone', 'preferred_lang', 'role', 'is_active', 'is_staff')
        }),
    )


@admin_site.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'line1', 'city', 'country', 'user', 'is_default', 'created_at')
    list_filter = ('country', 'is_default')
    search_fields = ('full_name', 'line1', 'city')
