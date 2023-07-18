from enum import Enum

from django.db import models

from site_account.user_management.models import User
from site_shop.order_management.models import Order
from site_shop.product_management.models import Product


class UserNotificationTemplate(Enum):
    ORDER = "سفارش"
    REFUND = "مرجوعی"
    COMMENT = "ثبت دیدگاه"


TEMPLATE_CHOICES = [(status.name, status.value) for status in UserNotificationTemplate]


class UserNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='notifications', blank=True, null=True)
    template = models.CharField(max_length=55, choices=TEMPLATE_CHOICES, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True, editable=False, blank=True, null=True)
    date_updated = models.DateTimeField(auto_now=True, editable=False, blank=True, null=True)
    is_delete = models.BooleanField(default=False)
