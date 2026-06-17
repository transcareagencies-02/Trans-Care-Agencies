from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from .utils import generate_receipt

@receiver(post_save, sender=Payment)
def create_receipt(sender, instance, created, **kwargs):
    if instance.status == "completed" and not instance.receipt:
        receipt = generate_receipt(instance)
        instance.receipt = receipt
        instance.save()