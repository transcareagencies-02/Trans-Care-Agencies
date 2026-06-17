from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('staff', 'Staff'),
    )

    CUSTOMER_TYPES = (
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('government', 'Government'),
    )

    phone = models.CharField(max_length=20, blank=True, null=True)

    county = models.CharField(max_length=100, blank=True, null=True)

    city = models.CharField(max_length=100, blank=True, null=True)

    postal_address = models.CharField(max_length=255, blank=True, null=True)

    company_name = models.CharField(max_length=255, blank=True, null=True)

    kra_pin = models.CharField(max_length=50, blank=True, null=True)

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='individual'
    )

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    newsletter = models.BooleanField(default=False)

    agreed_terms = models.BooleanField(default=False)

    agreed_privacy = models.BooleanField(default=False)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='customer'
    )
    
    otp = models.CharField(max_length=6, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = []
        # Make email unique
        constraints = [
            models.UniqueConstraint(fields=['email'], condition=models.Q(email__isnull=False), name='unique_email')
        ]

    def __str__(self):
        return self.username