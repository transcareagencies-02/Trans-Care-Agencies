from django.contrib import admin
from django.db.models import Sum, Count
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from datetime import timedelta
from .models import Order, OrderItem
from .models import Cart, CartItem
from products.models import Product, QuoteRequest


class CustomAdminSite(admin.AdminSite):
    site_header = "Transcare Control Center"
    site_title = "Transcare Admin"
    index_title = "Business Operations Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard))
        ]
        return custom_urls + urls

    def dashboard(self, request):
        total_sales = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        low_stock = Product.objects.filter(stock__lte=10).count()
        pending_quotes = QuoteRequest.objects.filter(status='pending').count()

        context = {
            "total_sales": total_sales,
            "low_stock": low_stock,
            "pending_quotes": pending_quotes,
        }

        return render(request, "admin/dashboard.html", context)


admin.site.__class__ = CustomAdminSite

admin.site.register(Cart)
admin.site.register(CartItem)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_amount', 'status', 'created_at')
    list_filter = (
        'status',
        'created_at',
    )
    search_fields = (
        'user__username',
        'phone',
    )
    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    actions = ['mark_processing', 'mark_delivered', 'total_orders']

    def mark_processing(self, request, queryset):
        queryset.update(status='processing')

    def mark_delivered(self, request, queryset):
        queryset.update(status='delivered')

    def total_orders(self, request, queryset):
        total = queryset.count()
        self.message_user(request, f"Total Orders: {total}")

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        total_sales = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        total_orders = Order.objects.count()

        pending_orders = Order.objects.filter(status='pending').count()

        extra_context['total_sales'] = total_sales
        extra_context['total_orders'] = total_orders
        extra_context['pending_orders'] = pending_orders

        return super().changelist_view(request, extra_context=extra_context)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_site.admin_view(self.dashboard_view))
        ]
        return custom_urls + urls

    def dashboard_view(self, request):
        today = timezone.now()

        # 📦 Basic stats
        total_orders = Order.objects.count()
        total_revenue = Order.objects.filter(status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0

        paid_orders = Order.objects.filter(status='paid').count()
        pending_orders = Order.objects.filter(status='pending').count()

        # 📈 Monthly data (last 6 months)
        months = []
        revenue_data = []

        for i in range(5, -1, -1):
            start_date = today - timedelta(days=30 * i)
            end_date = today - timedelta(days=30 * (i - 1)) if i > 0 else today

            monthly_revenue = Order.objects.filter(
                status='paid',
                created_at__range=[start_date, end_date]
            ).aggregate(total=Sum('total_amount'))['total'] or 0

            months.append(start_date.strftime("%b"))
            revenue_data.append(float(monthly_revenue))

        context = {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'paid_orders': paid_orders,
            'pending_orders': pending_orders,
            'months': months,
            'revenue_data': revenue_data,
        }

        return render(request, 'admin/dashboard.html', context)