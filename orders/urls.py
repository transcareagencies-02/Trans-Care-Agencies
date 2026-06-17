from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('export-sales/', views.export_sales, name='export_sales'),
]
