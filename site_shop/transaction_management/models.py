from enum import Enum
from random import randint

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

from site_account.user_management.models import User
from site_shop.order_management.models import Order


class TransactionStatus(Enum):
    SUCCESS = "پرداخت موفق"
    FAILED = "پرداخت ناموفق"


TRANSACTION_STATUS_CHOICES = [(status.name, status.value) for status in TransactionStatus]


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='transactions', blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='transactions', blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, blank=True, null=True)
    transaction_id = models.CharField(max_length=50, blank=True, null=True)  # شماره پیگیری
    slug = models.SlugField(max_length=6, unique=True, blank=True, null=True)

    ref_id = models.CharField(max_length=255, blank=True, null=True)
    reason = models.TextField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)

    def save(self, *args, **kwargs):

        if self.transaction_id is None:
            transaction_id = randint(10000000, 99999999)
            while Transaction.objects.filter(transaction_id=transaction_id).exists():
                transaction_id = randint(10000000, 99999999)
            self.transaction_id = transaction_id
        if self.slug is None:
            slug = get_random_string(6)
            while Transaction.objects.filter(slug=slug).exists():
                slug = get_random_string(6)

            self.slug = slug

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['order'], condition=models.Q(status=TransactionStatus.SUCCESS.name),
                                    name='unique_successful_transaction')
        ]

    def clean(self):
        if self.status == TransactionStatus.SUCCESS.name and self.order.transactions.filter(
                status=TransactionStatus.SUCCESS.name).exists():
            raise ValidationError("An order can have only one successful transaction.")

    def __str__(self):
        return f"Transaction for Order #{self.order_id}: {self.transaction_id}"
