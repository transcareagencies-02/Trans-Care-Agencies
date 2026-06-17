from django.urls import path
from . import views

urlpatterns = [
    path("", views.quote_home, name="quote_home"),
    path("success/", views.quote_success, name="quote_success"),
    path("admin/update-status/<int:quote_id>/", views.update_quote_status, name="update_quote_status"),
]