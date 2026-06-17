from django.shortcuts import render
from django.shortcuts import get_object_or_404

from orders.models import Cart
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import F, Sum
from django.utils import timezone
from datetime import timedelta

from products.models import Product, QuoteRequest
from products.forms import ProductForm
from orders.models import Order
from payments.models import Payment
from users.models import User


@staff_member_required
def admin_users(request):
    """Simple staff-only user list/profile view for admin dashboard."""
    users = User.objects.order_by('-date_joined')

    return render(request, 'admin/users.html', {'users': users})


@staff_member_required
def admin_user_detail(request, user_id):
    user_obj = get_object_or_404(User, id=user_id)

    # allow simple admin actions via POST
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            user_obj.is_verified = True
            user_obj.save()
            messages.success(request, 'User marked as verified.')
            return redirect('admin_user_detail', user_id=user_id)

        if action == 'toggle_active':
            user_obj.is_active = not user_obj.is_active
            user_obj.save()
            messages.success(request, 'User active status updated.')
            return redirect('admin_user_detail', user_id=user_id)

        if action == 'set_role':
            new_role = request.POST.get('role')
            if new_role in dict(User.ROLE_CHOICES).keys():
                user_obj.role = new_role
                user_obj.save()
                messages.success(request, 'User role updated.')
            return redirect('admin_user_detail', user_id=user_id)

    user_orders = Order.objects.filter(user=user_obj)
    user_payments = Payment.objects.filter(user=user_obj)

    return render(request, 'admin/user_detail.html', {
        'user_obj': user_obj,
        'orders': user_orders,
        'payments': user_payments,
    })


def home(request):
    items = []

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = cart.items.all()

    return render(request, "home.html", {"items": items})

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')


@login_required
def customer_dashboard(request):
    orders = Order.objects.filter(user=request.user).select_related('payment').order_by('-created_at')
    payments = Payment.objects.filter(user=request.user).order_by('-payment_date')
    quote_requests = QuoteRequest.objects.filter(user=request.user).order_by('-created_at')

    total_orders = orders.count()
    total_spent = payments.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    total_payments = payments.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'dashboard/customer_dashboard.html', {
        'orders': orders,
        'payments': payments,
        'quote_requests': quote_requests,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'total_payments': total_payments,
    })


@login_required
def dashboard(request):
    if request.user.role == 'customer':
        return customer_dashboard(request)

    if not (request.user.is_staff or request.user.role in ['admin', 'staff']):
        messages.warning(request, 'Dashboard is not available for your account type.')
        return redirect('home')

    # Product creation form
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully')
            return redirect('admin_dashboard')
    else:
        form = ProductForm()

    product_count = Product.objects.count()
    low_stock_count = Product.objects.filter(stock__lte=F('reorder_level')).count()
    user_count = User.objects.count()
    verified_users = User.objects.filter(is_verified=True).count()

    payment_count = Payment.objects.count()
    total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
    completed_payments = Payment.objects.filter(status='completed').count()
    pending_bank_verifications = Payment.objects.filter(method='bank', status='pending').count()
    verified_bank_transfers = Payment.objects.filter(method='bank', verified_at__isnull=False).count()

    # sales/orders per day for last 7 days
    today = timezone.now().date()
    labels = []
    data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        labels.append(day.strftime('%b %d'))
        total = Order.objects.filter(created_at__date=day).count()
        data.append(total)

    recent_orders = Order.objects.order_by('-created_at')[:6]
    recent_payments = Payment.objects.order_by('-payment_date')[:6]
    quote_requests = QuoteRequest.objects.select_related('user', 'product').order_by('-created_at')

    context = {
        'form': form,
        'product_count': product_count,
        'low_stock_count': low_stock_count,
        'user_count': user_count,
        'verified_users': verified_users,
        'payment_count': payment_count,
        'total_revenue': total_revenue,
        'completed_payments': completed_payments,
        'pending_bank_verifications': pending_bank_verifications,
        'verified_bank_transfers': verified_bank_transfers,
        'chart_labels': labels,
        'chart_data': data,
        'recent_orders': recent_orders,
        'recent_payments': recent_payments,
        'quote_requests': quote_requests,
    }

    return render(request, 'admin/dashboard.html', context)