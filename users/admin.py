from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone',
        'county',
        'city',
        'company_name',
        'customer_type',
        'role'
    )
    search_fields = (
        'username',
        'email',
        'phone',
        'company_name',
        'county',
        'city'
    )
    list_filter = ('role', 'customer_type')