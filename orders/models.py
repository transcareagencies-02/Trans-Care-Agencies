from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from core.email_utils import add_email_footer
from users.models import User
from products.models import Product
from django.conf import settings


class Order(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    customer_kra_pin = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    is_paid = models.BooleanField(
        default=False
    )

    delivery_address = models.TextField()

    phone = models.CharField(
        max_length=20
    )

    accepted_terms = models.BooleanField(
        default=False
    )

    accepted_privacy = models.BooleanField(
        default=False
    )

    accepted_warranty = models.BooleanField(
        default=False
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    def save(self, *args, **kwargs):
        old_status = None
        if self.pk:
            old_status = Order.objects.filter(pk=self.pk).values_list('status', flat=True).first()

        super().save(*args, **kwargs)

        if old_status and old_status != self.status and getattr(self.user, 'email', None):
            status_label = self.get_status_display().replace('Pending Payment', 'Pending')
            EmailMessage(
                subject=f"Order #{self.id} status updated to {status_label}",
                body=add_email_footer(
                    f"""
Dear {self.user.username},

Your order #{self.id} has been updated to {status_label}.

Thank you for shopping with Trans Care Agencies.

Regards,
Trans Care Order Management
"""
                ),
                from_email=settings.ORDERS_EMAIL,
                to=[self.user.email],
            ).send(fail_silently=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def get_total_price(self):
        return self.quantity * self.price


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart - {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.quantity * self.product.price