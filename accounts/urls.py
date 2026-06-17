from django.urls import path
from . import views
from .views import export_sales_csv

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-users/', views.admin_users, name='admin_users'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    path('export-sales-csv/', export_sales_csv, name='export_sales_csv'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]