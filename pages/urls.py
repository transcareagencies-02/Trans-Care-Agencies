from django.urls import path
from . import views

urlpatterns = [
    path('faqs/', views.faqs, name='faqs'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    path('warranty/', views.warranty, name='warranty'),
]