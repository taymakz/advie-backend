from enum import Enum

from django.db import models

from site_shop.order_management.models import OrderItem


class RefundStatus(Enum):
    NOT_REQUESTED = "درخواست نشده"
    PENDING = "در انتظار تایید"
    ACCEPTED = "تایید شده"
    REJECTED = "درخواست رد شد"


REFUND_STATUS_CHOICES = [(status.name, status.value) for status in RefundStatus]


class RefundOrderItem(models.Model):
    order_item = models.OneToOneField(OrderItem, on_delete=models.DO_NOTHING, related_name="refund")
    status = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, default=RefundStatus.NOT_REQUESTED.value)
    reject_message = models.TextField(blank=True, null=True)

    date_requested = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_status = self.status

    def clean(self):
        self._previous_status = self.status

    def save(self, *args, **kwargs):
        if self.status != self._previous_status:

            if self.status == RefundStatus.PENDING.value:
                import datetime
                self.date_requested = datetime.date.today()
            if self.status == RefundStatus.ACCEPTED.value:
                print('Send SMS In ORDER')
            if self.status == RefundStatus.REJECTED.value:
                print('Send SMS In ORDER')
            elif self.status == 'sent':
                import datetime
                self.shipped_date = datetime.date.today()
                print('Send SMS In ORDER')
            self._previous_status = self.status
        super().save(*args, **kwargs)

    def send_refund_status_notification(self, pattern):
        # celery_send_order_status_service.delay(to=self.user.phone, pattern=pattern, id=self.transaction)
        pass
