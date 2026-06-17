from django.db import models
from products.models import Product


class QuoteRequest(models.Model):

    STATUS_CHOICES = (
        ("new", "New"),
        ("reviewing", "Reviewing"),
        ("quoted", "Quoted"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="quote_requests"
    )

    company_name = models.CharField(
        max_length=255
    )

    contact_person = models.CharField(
        max_length=255
    )

    phone = models.CharField(
        max_length=20
    )

    email = models.EmailField()

    quantity = models.PositiveIntegerField()

    delivery_location = models.CharField(
        max_length=255,
        blank=True
    )

    budget = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )

    message = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.company_name} - {self.product.name}"