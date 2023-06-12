from enum import Enum
from random import randint

from django.core.exceptions import ValidationError
from django.db import models

from site_account.user_management.models import User
from site_shop.order_management.models import Order


class TransactionStatus(Enum):
    SUCCESS = "تراکنش موفق"
    FAILED = "تراکنش ناموفق"


TRANSACTION_STATUS_CHOICES = [(status.name, status.value) for status in TransactionStatus]


class TransactionManager(models.Manager):
    def get_success(self):
        return self.filter(status=TransactionStatus.SUCCESS.value)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='transactions', blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, related_name='transactions', blank=True, null=True)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, blank=True, null=True)
    transaction_id = models.CharField(max_length=50)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    objects = TransactionManager()
    def save(self, *args, **kwargs):
        if self.transaction_id is None and self.status == TransactionStatus.SUCCESS.value:
            transaction_id = randint(10000000, 99999999)
            while Transaction.objects.filter(transaction=transaction_id).exists():
                transaction_id = randint(10000000, 99999999)
            self.transaction = transaction_id

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
