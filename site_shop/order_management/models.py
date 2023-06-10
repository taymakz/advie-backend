from random import randint

from django.db import models

from site_account.user_management.models import User
from site_shop.coupon_management.models import Coupon
from site_shop.shipping_management.models import ShippingPrice


class OrderAddress(models.Model):
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=11)
    receiver_city = models.CharField(max_length=100)
    receiver_province = models.CharField(max_length=100)
    receiver_postal_code = models.CharField(max_length=100)
    receiver_address = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.receiver_name} {self.receiver_phone}"
class OrderStatus(models.Model):
    pass

class Order(models.Model):
    STATUS_CHOICES = (
        ('canceled', 'لغو شده'),
        ('pending', 'در انتظار تایید'),
        ('processing', 'درحال پردازش'),
        ('shipped', 'ارسال شد'),
        ('delivered', 'تحویل داده شده'),
    )
    user = models.ForeignKey(User,on_delete=models.SET_NULL,related_name='orders', blank=True, null=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, blank=True, null=True)

    shipping = models.ForeignKey(ShippingPrice, on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.SET_NULL, blank=True, null=True)
    is_paid = models.BooleanField(default=False)

    transaction = models.CharField(max_length=100, blank=True, null=True)
    tracking_code = models.CharField(max_length=100, blank=True, null=True)

    coupon_effect_price = models.IntegerField(null=True, blank=True)
    shipping_effect_price = models.IntegerField(null=True, blank=True)

    date_ordered = models.DateTimeField(blank=True, null=True)
    date_shipped = models.DateTimeField(blank=True, null=True)
    date_delivered = models.DateTimeField(blank=True, null=True)

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    class Meta:
        ordering = ['-date_ordered']

    def __str__(self):
        return f"{self.user.username} - {self.transaction} - {self.get_status_display()} : {self.is_paid}"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._previous_status = self.status

    def clean(self):
        self._previous_status = self.status

    def save(self, *args, **kwargs):
        if self.transaction is None and self.is_paid:
            transaction_id = randint(10000000, 99999999)
            while Order.objects.filter(transaction=transaction_id).exists():
                transaction_id = randint(10000000, 99999999)
            self.transaction = transaction_id
        if self.status != self._previous_status:

            if self.status == 'pending':
                print('Send SMS In ORDER')
                # celery_send_order_status_service.delay(to=self.user.phone, pattern='rczcnmv3pgodhte', id=self.transaction)
            if self.status == 'processing':
                print('Send SMS In ORDER')
                # celery_send_order_status_service.delay(to=self.user.phone, pattern='z0lefyrpe670s58', id=self.transaction)

            elif self.status == 'sent':
                import datetime
                self.shipped_date = datetime.date.today()
                print('Send SMS In ORDER')
                # celery_send_order_status_service.delay(to=self.user.phone, pattern='ygg1nm5hlhfi50c', id=self.transaction)
            self._previous_status = self.status
        super().save(*args, **kwargs)

    def is_valid_shipping_method(self, user_main_address, shipping):
        # Get the ShippingPrice object with the given ID

        if shipping.area == 'همه':
            # Filter all ShippingPrice objects that are active and not equal to 'همه'
            other_shipping_areas = ShippingPrice.objects.filter(~Q(area='همه'), is_active=True)
            if user_main_address and user_main_address.province in [shipping_area.area for shipping_area in
                                                                    other_shipping_areas]:
                # User's main address province matches an active shipping area
                message = 'شیوه ارسال انتخاب شده نا معتبر است'
                return False, message
            else:
                return True, None
        else:
            if user_main_address and user_main_address.province == shipping.area:
                # User's main address province matches the shipping area
                return True, None
            else:
                message = 'شیوه ارسال انتخاب شده نا معتبر است'
                return False, message

    @property
    def get_total_price(self):
        amount = 0
        if self.is_paid:
            for item in self.items.all():
                amount += item.final_price
            if self.coupon_effect_price is not None:
                amount -= self.coupon_effect_price
        else:
            for item in self.items.all():
                amount += item.get_total_price
            # if self.coupon and self.coupon.validate_coupon(order_total_price=amount, user_id=self.user.id):
            #     new_price, dif_price = self.coupon.calculate_discount(amount)
            #     amount -= dif_price
        return amount

    @property
    def get_total_profit(self):
        profit = 0
        profit += self.coupon_effect_price or 0
        if self.is_paid:
            for item in self.items.all():
                profit += item.final_profit
        return profit

    @property
    def get_total_price_before_discount(self):
        amount = 0
        for item in self.items.all():
            amount += item.final_price_before_discount
        return amount
