from django.contrib import admin
from django.utils import timezone
from config.admin import admin_site
from .models import Coupon, Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price_at_purchase', 'total', 'product_snapshot')
    fields = ('product', 'quantity', 'unit_price_at_purchase', 'total', 'product_snapshot')


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


@admin_site.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'discount_type', 'discount_value', 'uses_count', 'max_uses',
        'is_active', 'valid_from', 'valid_until', 'created_at',
    )
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
    list_editable = ('is_active',)
    list_per_page = 25
    readonly_fields = ('uses_count', 'created_at', 'updated_at')


@admin_site.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'public_id', 'customer_name', 'customer_phone', 'status', 'total',
        'created_at', 'user',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('public_id', 'customer_name', 'customer_phone', 'customer_email', 'user__email')
    list_editable = ('status',)
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline, PaymentInline]
    list_per_page = 25
    readonly_fields = (
        'public_id', 'subtotal', 'discount_amount', 'tax_amount', 'shipping_amount',
        'total', 'paid_at', 'fulfilled_at', 'created_at', 'updated_at',
    )


@admin_site.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'provider', 'status', 'amount', 'external_id', 'created_at')
    list_filter = ('provider', 'status')
    search_fields = ('order__public_id', 'external_id')
