from django.db import models
from orders.models import Order
from django.conf import settings

class Payment(models.Model):
    PAYMENT_METHODS = (
        ('mpesa', 'M-Pesa'),
        ('bank', 'Bank Transfer'),
    )

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=10, choices=PAYMENT_METHODS)

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    transaction_id = models.CharField(max_length=255, blank=True, null=True)  # M-Pesa code
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    bank_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    proof_of_payment = models.FileField(
        upload_to="bank_proofs/",
        blank=True,
        null=True
    )

    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_payments"
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    checkout_request_id = models.CharField(max_length=255, blank=True, null=True)
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id}"