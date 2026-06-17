from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'method', 'status', 'transaction_id', 'payment_date')
    list_filter = ('status', 'method')
    search_fields = ('transaction_id',)

    actions = ['mark_completed', 'mark_failed']

    def mark_completed(self, request, queryset):
        queryset.update(status='completed')

    def mark_failed(self, request, queryset):
        queryset.update(status='failed')