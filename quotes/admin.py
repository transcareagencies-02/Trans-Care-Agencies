from django.contrib import admin
from .models import QuoteRequest


@admin.register(QuoteRequest)
class QuoteAdmin(admin.ModelAdmin):

    list_display = (
        'company_name',
        'contact_person',
        'product',
        'phone',
        'email',
        'quantity',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'created_at'
    )

    search_fields = (
        'company_name',
        'contact_person',
        'email',
        'phone'
    )