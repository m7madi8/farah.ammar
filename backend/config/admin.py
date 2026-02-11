"""
Custom AdminSite for Chef Farah Ammar: admin-only access (role admin/super_admin),
analytics on index page, production-ready dashboard.
Import of orders.models is deferred to avoid circular import with app admins.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils import timezone
from django.db.models import Sum
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from decimal import Decimal


class NanaBitesAdminSite(AdminSite):
    site_header = "Chef Farah Ammar"
    site_title = "Chef Farah Ammar"
    index_title = "لوحة التحكم"
    index_template = 'admin/dashboard_index.html'

    def get_analytics(self):
        """Aggregate stats for dashboard: sales, best-sellers, active orders, coupons. Returns None on error."""
        try:
            from orders.models import Order, OrderItem, Coupon
        except Exception:
            return None
        try:
            now = timezone.now()
            revenue_statuses = ['paid', 'processing', 'shipped', 'delivered']
            qs_revenue = Order.objects.filter(status__in=revenue_statuses)
            total_sales_all = qs_revenue.aggregate(s=Sum('total'))['s'] or Decimal('0')
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily = Order.objects.filter(
                status__in=revenue_statuses,
                created_at__gte=today_start,
            ).aggregate(s=Sum('total'))['s'] or Decimal('0')
            from datetime import timedelta
            week_start = now - timedelta(days=7)
            weekly = Order.objects.filter(
                status__in=revenue_statuses,
                created_at__gte=week_start,
            ).aggregate(s=Sum('total'))['s'] or Decimal('0')
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly = Order.objects.filter(
                status__in=revenue_statuses,
                created_at__gte=month_start,
            ).aggregate(s=Sum('total'))['s'] or Decimal('0')
            active_statuses = ['pending', 'confirmed', 'paid', 'processing', 'shipped']
            active_orders_count = Order.objects.filter(status__in=active_statuses).count()
            best_sellers = (
                OrderItem.objects.filter(order__status__in=revenue_statuses)
                .values('product_id', 'product__name_en')
                .annotate(total_qty=Sum('quantity'))
                .order_by('-total_qty')[:10]
            )
            coupons_used = Coupon.objects.aggregate(s=Sum('uses_count'))['s'] or 0
            orders_with_coupon = Order.objects.filter(coupon__isnull=False).count()
            return {
                'total_sales_all': total_sales_all,
                'sales_daily': daily,
                'sales_weekly': weekly,
                'sales_monthly': monthly,
                'active_orders_count': active_orders_count,
                'best_sellers': list(best_sellers),
                'coupons_uses_total': coupons_used,
                'orders_with_coupon': orders_with_coupon,
            }
        except Exception:
            return None

    @method_decorator(never_cache)
    def index(self, request, extra_context=None):
        extra_context = extra_context or {}
        if request.user.is_authenticated:
            role = getattr(request.user, 'role', None)
            if role in ('admin', 'super_admin') or request.user.is_superuser:
                analytics = self.get_analytics()
                if analytics is not None:
                    extra_context['analytics'] = analytics
        return super().index(request, extra_context)

    def has_permission(self, request):
        """Only admin and super_admin roles (and superuser) can access the dashboard."""
        if not request.user.is_active:
            return False
        if request.user.is_superuser:
            return True
        return getattr(request.user, 'role', None) in ('admin', 'super_admin')


# Use our custom site
admin_site = NanaBitesAdminSite(name='admin')
