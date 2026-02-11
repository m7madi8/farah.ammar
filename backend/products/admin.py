from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, ProductCategory, InventoryLog


# ---------- Filters ----------
class CategoryListFilter(admin.SimpleListFilter):
    title = 'category'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        return [(c.id, c.name_en) for c in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(product_category_links__category_id=self.value()).distinct()
        return queryset


class LowStockListFilter(admin.SimpleListFilter):
    title = 'stock alert'
    parameter_name = 'stock'

    def lookups(self, request, model_admin):
        return [
            ('low', 'Low stock (≤5)'),
            ('out', 'Out of stock (0)'),
            ('ok', 'In stock (>5)'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'low':
            return queryset.filter(stock_quantity__lte=5, stock_quantity__gt=0)
        if self.value() == 'out':
            return queryset.filter(stock_quantity=0)
        if self.value() == 'ok':
            return queryset.filter(stock_quantity__gt=5)
        return queryset


class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory
    extra = 0


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name_en', 'sort_order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name_en', 'name_ar', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'slug', 'name_en', 'sku', 'price', 'stock_display', 'is_active', 'created_at',
    )
    list_filter = ('is_active', LowStockListFilter, CategoryListFilter)
    search_fields = ('name_en', 'name_ar', 'sku', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    inlines = [ProductCategoryInline, ProductImageInline]
    list_per_page = 25

    @admin.display(description='Stock')
    def stock_display(self, obj):
        if obj.stock_quantity <= 0:
            return format_html('<span style="color: red;">Out (0)</span>')
        if obj.stock_quantity <= 5:
            return format_html('<span style="color: orange;">{} (low)</span>', obj.stock_quantity)
        return obj.stock_quantity


class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'change_qty', 'quantity_after', 'reason', 'reference_type', 'created_at')
    list_filter = ('reason',)
    search_fields = ('product__name_en',)
    readonly_fields = (
        'product', 'change_qty', 'quantity_after', 'reason',
        'reference_type', 'reference_id', 'notes', 'created_at', 'created_by',
    )


# Register with custom admin site (after it's fully loaded to avoid circular import)
from config.admin import admin_site
admin_site.register(Category, CategoryAdmin)
admin_site.register(Product, ProductAdmin)
admin_site.register(InventoryLog, InventoryLogAdmin)
