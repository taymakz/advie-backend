from enum import Enum

from django.db import models

from site_account.user_management.models import User


class UserNotificationTemplate(Enum):
    ORDER = "سفارش"
    REFUND = "مرجوعی"
    COMMENT = "ثبت دیدگاه"


TEMPLATE_CHOICES = [(status.name, status.value) for status in UserNotificationTemplate]


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.CharField(max_length=55, choices=TEMPLATE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=255)
    link = models.URLField()

    is_read = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)
