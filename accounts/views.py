from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages

from .forms import RegisterForm
from orders.models import Order
from payments.models import Payment
from products.models import Product, QuoteRequest

from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.db import models
from datetime import datetime

from django.http import HttpResponse
import csv
from django.contrib import messages
from .forms import ProfileUpdateForm
from .forms import CustomPasswordChangeForm
from .models import OTP


def generate_otp(existing_code=None):
    while True:
        otp = str(random.randint(100000, 999999))
        if existing_code is None or otp != str(existing_code):
            return otp


def send_verification_email(user, otp):
    message = add_email_footer(f"""
Dear {user.username},

Thank you for creating an account with Trans Care Agencies.
Please use the verification code below to complete your registration.

Verification Code: {otp}

This code will expire in 10 minutes.

If you did not request this code, please ignore this email.

Regards,
Trans Care Account Security
""")

    send_mail(
        subject="Verify Your Trans Care Account",
        message=message,
        from_email=settings.SECURITY_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from core.email_utils import add_email_footer
import random
from users.models import User


# =========================
# AUTH VIEWS
# =========================

def register_view(request):

    # IF USER ALREADY LOGGED IN
    if request.user.is_authenticated:
        return redirect('products')

    form = RegisterForm(request.POST or None, request.FILES or None)

    if request.method == "POST":

        if form.is_valid():

            # CREATE USER BUT DON'T SAVE YET
            user = form.save(commit=False)

            # GENERATE OTP
            otp = generate_otp(user.otp)

            # SAVE OTP
            user.otp = otp

            # DEACTIVATE ACCOUNT UNTIL VERIFIED
            user.is_active = False
            user.is_verified = False

            # SAVE USER
            user.save()

            # SEND OTP EMAIL
            send_verification_email(user, otp)

            # STORE EMAIL IN SESSION
            request.session['email'] = user.email

            messages.success(
                request,
                "Verification OTP sent to your email."
            )

            return redirect('accounts:verify_otp')

        else:
            messages.error(request, "Please correct the errors below.")

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def login_view(request):

    # IF ALREADY LOGGED IN
    if request.user.is_authenticated:
        return redirect('admin_dashboard')

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        # USER EXISTS
        if user is not None:

            # CHECK VERIFIED
            if not user.is_active:

                messages.error(
                    request,
                    "Please verify your email first."
                )

                return redirect('accounts:verify_otp')

            login(request, user)

            messages.success(
                request,
                f"Welcome back {user.username}"
            )

            return redirect('admin_dashboard')

        else:

            error = "Invalid username or password"
            messages.error(
                request,
                error
            )

    return render(request, "accounts/login.html", {"error": error})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('/')



def edit_profile(request):
    user = request.user

    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()

            messages.success(request, "Profile updated successfully ✅")
            return redirect('edit_profile')   # reload page after save
    else:
        form = ProfileUpdateForm(instance=user)

    return render(request, 'accounts/edit_profile.html', {'form': form})

@login_required
def send_otp(request):
    otp = generate_otp(request.user.otp)
    request.user.otp = otp
    request.user.save(update_fields=['otp'])

    OTP.objects.create(user=request.user, code=otp)
    send_verification_email(request.user, otp)

    messages.success(request, "A new verification code has been sent to your email.")

    return redirect('accounts:verify_otp')


def resend_otp(request):
    email = request.session.get('email') or getattr(request.user, 'email', None)

    if not email:
        messages.error(request, "Session expired. Please register again.")
        return redirect('accounts:register')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('accounts:register')

    otp = generate_otp(user.otp)
    user.otp = otp
    user.save(update_fields=['otp'])

    OTP.objects.create(user=user, code=otp)
    send_verification_email(user, otp)

    messages.success(request, "A fresh verification code has been sent to your email.")

    return redirect('accounts:verify_otp')

def verify_otp(request):

    # GET EMAIL FROM SESSION
    email = request.session.get('email')

    if not email:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')

    try:
        user = User.objects.get(email=email)

    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('register')
    
    except User.MultipleObjectsReturned:
        messages.error(request, "Database error: Multiple accounts with this email found. Please contact support.")
        return redirect('register')

    if request.method == "POST":

        otp = (request.POST.get('otp') or request.POST.get('code') or '').strip()

        # VERIFY OTP
        if user.otp and str(user.otp).strip() == otp:

            user.is_verified = True
            user.is_active = True
            user.otp = ""

            user.save()

            # OPTIONAL AUTO LOGIN
            login(request, user)

            # CLEAR SESSION
            del request.session['email']

            messages.success(
                request,
                "Account verified successfully."
            )

            return redirect('admin_dashboard')

        else:
            messages.error(request, "Invalid OTP code.")

    return render(request, "accounts/verify_otp.html")

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()

            # 🔥 Keep user logged in after password change
            update_session_auth_hash(request, user)

            messages.success(request, "✅ Password updated successfully")
            return redirect('admin_dashboard')

    else:
        form = CustomPasswordChangeForm(user=request.user)
    
     # 🚨 BLOCK if OTP not verified
    if not request.session.get('otp_verified'):
        return redirect('send_otp')

    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)

            # reset OTP session
            request.session['otp_verified'] = False

            return redirect('admin_dashboard')

    else:
        form = CustomPasswordChangeForm(user=request.user)

    return render(request, 'accounts/change_password.html', {'form': form})

# =========================
# ADMIN DASHBOARD
# =========================

@staff_member_required
def admin_dashboard(request):

    # 💰 TOTAL REVENUE (Completed payments only)
    revenue = Payment.objects.filter(status="Completed").aggregate(
        total=Sum('amount')
    )['total'] or 0

    # 📦 TOTAL ORDERS
    total_orders = Order.objects.count()

    # 💳 PAYMENT STATS
    paid = Payment.objects.filter(status="Completed").count()
    pending = Payment.objects.filter(status="Pending").count()

    # 📊 SALES OVER TIME
    sales_data = (
        Payment.objects.filter(status="Completed")
        .annotate(date=TruncDate('payment_date'))
        .values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    # 🏆 TOP PRODUCTS
    top_products = (
        Product.objects.annotate(total_sold=Count('orderitem'))
        .order_by('-total_sold')[:5]
    )

    quote_requests = QuoteRequest.objects.select_related('user', 'product').order_by('-created_at')

    context = {
        "revenue": revenue,
        "total_orders": total_orders,
        "paid": paid,
        "pending": pending,
        "sales_data": list(sales_data),
        "top_products": top_products,
        "quote_requests": quote_requests,
    }

    return render(request, "admin/dashboard.html", context)


# =========================
# EXPORT CSV
# =========================

@staff_member_required
def export_sales_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Order ID', 'User', 'Amount', 'Status', 'Date'])

    orders = Order.objects.select_related('user').all()

    for order in orders:
        writer.writerow([
            order.id,
            order.user.username if order.user else "N/A",
            order.total_amount,
            order.status,
            order.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])

    return response


# =========================
# ADMIN: USERS MANAGEMENT
# =========================

@staff_member_required
def admin_users(request):
    users = User.objects.all().order_by('-date_joined')
    total_users = users.count()
    individual_customers = users.filter(customer_type='individual').count()
    business_customers = users.filter(customer_type='business').count()
    government_customers = users.filter(customer_type='government').count()

    context = {
        "users": users,
        "total_users": total_users,
        "individual_customers": individual_customers,
        "business_customers": business_customers,
        "government_customers": government_customers,
    }

    return render(request, "admin/users.html", context)


# =========================
# ADMIN: ORDERS MANAGEMENT
# =========================

@staff_member_required
def admin_orders(request):
    orders = Order.objects.select_related('user').all().order_by('-created_at')
    total_orders = orders.count()
    pending_orders = orders.filter(status='pending').count()
    paid_orders = orders.filter(status='paid').count()
    processed_orders = orders.filter(status='processing').count()
    delivered_orders = orders.filter(status='delivered').count()

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "paid_orders": paid_orders,
        "processed_orders": processed_orders,
        "delivered_orders": delivered_orders,
    }

    return render(request, "admin/orders.html", context)


# =========================
# ADMIN: ANALYTICS & REPORTS
# =========================

@staff_member_required
def admin_analytics(request):
    # ========== ORDERS ==========
    total_orders = Order.objects.count()
    orders_this_month = Order.objects.filter(
        created_at__month=datetime.now().month,
        created_at__year=datetime.now().year
    ).count()

    # ========== REVENUE ==========
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0

    revenue_this_month = Payment.objects.filter(
        status='completed',
        payment_date__month=datetime.now().month,
        payment_date__year=datetime.now().year
    ).aggregate(total=Sum('amount'))['total'] or 0

    # ========== PAYMENTS ==========
    total_payments = Payment.objects.count()
    completed_payments = Payment.objects.filter(status='completed').count()
    pending_payments = Payment.objects.filter(status='pending').count()
    failed_payments = Payment.objects.filter(status='failed').count()

    # ========== CUSTOMERS ==========
    total_customers = User.objects.filter(role='customer').count()
    new_customers_this_month = User.objects.filter(
        role='customer',
        date_joined__month=datetime.now().month,
        date_joined__year=datetime.now().year
    ).count()

    # ========== TOP PRODUCTS ==========
    from orders.models import OrderItem
    top_products = (
        Product.objects.annotate(
            total_sold=Count('orderitem'),
            total_revenue=Sum('orderitem__quantity')
        )
        .order_by('-total_sold')[:5]
    )

    # ========== PAYMENT METHODS ==========
    payment_methods = Payment.objects.values('method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )

    context = {
        "total_orders": total_orders,
        "orders_this_month": orders_this_month,
        "total_revenue": total_revenue,
        "revenue_this_month": revenue_this_month,
        "total_payments": total_payments,
        "completed_payments": completed_payments,
        "pending_payments": pending_payments,
        "failed_payments": failed_payments,
        "total_customers": total_customers,
        "new_customers_this_month": new_customers_this_month,
        "top_products": top_products,
        "payment_methods": payment_methods,
    }

    return render(request, "admin/analytics.html", context)