from django.contrib import admin
from django.db.models import Sum
from django.db import models

from .models import (
    Product,
    Category,
    QuoteRequest,
    ProductImage,
    ProductSpecification,
    ProductReview,
    ProductDocument
)


# =========================
# INLINE MODELS
# =========================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


class ProductReviewInline(admin.TabularInline):
    model = ProductReview
    extra = 1


class ProductDocumentInline(admin.TabularInline):
    model = ProductDocument
    extra = 1


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'category',
        'price',
        'product_type',
        'stock',
        'stock_status',
        'is_active'
    )

    list_filter = (
        'product_type',
        'category',
        'is_active'
    )

    search_fields = ('name',)

    list_editable = (
        'price',
        'stock',
        'is_active'
    )

    # REMOVE THIS:
    # prepopulated_fields = {"name": ("name",)}

    inlines = [
        ProductImageInline,
        ProductSpecificationInline,
        ProductReviewInline,
        ProductDocumentInline
    ]

    actions = [
        'mark_active',
        'mark_inactive',
        'mark_out_of_stock',
        'restock_50',
        'restock_100'
    ]

    # =========================
    # STOCK STATUS
    # =========================

    def stock_status(self, obj):
        if obj.stock <= obj.reorder_level:
            return "⚠ LOW STOCK"
        return "✅ OK"

    stock_status.short_description = "Stock Status"

    # =========================
    # ACTIONS
    # =========================

    def mark_active(self, request, queryset):
        queryset.update(is_active=True)

    mark_active.short_description = "Mark selected products as active"

    def mark_inactive(self, request, queryset):
        queryset.update(is_active=False)

    mark_inactive.short_description = "Mark selected products as inactive"

    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock=0)

    mark_out_of_stock.short_description = "Set stock to 0"

    def restock_50(self, request, queryset):
        for product in queryset:
            product.stock += 50
            product.save()

    restock_50.short_description = "Add 50 stock"

    def restock_100(self, request, queryset):
        for product in queryset:
            product.stock += 100
            product.save()

    restock_100.short_description = "Add 100 stock"


# =========================
# CATEGORY ADMIN
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ('name',)


# =========================
# QUOTE REQUEST ADMIN
# =========================

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):

    list_display = (
        'institution_name',
        'product',
        'quantity',
        'status',
        'created_at'
    )

    list_filter = (
        'status',
        'created_at'
    )

    search_fields = (
        'institution_name',
        'phone',
        'email'
    )

    readonly_fields = ('created_at',)

    actions = [
        'mark_reviewed',
        'mark_quoted'
    ]

    def mark_reviewed(self, request, queryset):
        queryset.update(status='reviewed')

    mark_reviewed.short_description = "Mark selected as reviewed"

    def mark_quoted(self, request, queryset):
        queryset.update(status='quoted')

    mark_quoted.short_description = "Mark selected as quoted"