from django.conf import settings
from django.db import models


class ChatSession(models.Model):

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    assigned_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="staff_chats"
    )

    status = models.CharField(
        max_length=20,
        default="open"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )


class ChatMessage(models.Model):

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )