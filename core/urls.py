from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.contrib.auth import views as auth_views
from core import views as core_views


def home(request):
    return render(request, "home.html")

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('orders/', include('orders.urls')),
    path('payments/', include('payments.urls')),
    path('products/', include('products.urls')),
    path('quotes/', include('quotes.urls')),
    path('cart/', include('cart.urls')),
    path('pages/', include('pages.urls')),
    path('accounts/', include('accounts.urls')),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path(
        "chatbot/",
        include("chatbot.urls")
    ),
    path('dashboard/', core_views.dashboard, name='admin_dashboard'),
    path('dashboard/users/', core_views.admin_users, name='admin_users'),
    path('dashboard/users/<int:user_id>/', core_views.admin_user_detail, name='admin_user_detail'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:login')
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)