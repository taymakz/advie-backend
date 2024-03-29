from datetime import timedelta
from enum import Enum

from django.db import models
from django.utils import timezone

from site_account.user_addresses.models import UserAddresses
from site_account.user_management.models import User
from site_api.api_configuration.enums import ResponseMessage
from site_notification.user_notification import models as notificationModels
from site_shop.coupon_management.models import Coupon
from site_shop.product_management.models import Product, ProductVariant
from site_shop.refund_management.models import RefundOrderItem
from site_shop.shipping_management.models import ShippingRate
from site_utils.messaging_services.phone_service import send_order_status_phone


class OrderAddress(models.Model):
    receiver_name = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=11)
    receiver_city = models.CharField(max_length=100)
    receiver_province = models.CharField(max_length=100)
    receiver_postal_code = models.CharField(max_length=100)
    receiver_address = models.CharField(max_length=300)
    receiver_national_code = models.CharField(max_length=11)

    def __str__(self):
        return f"{self.receiver_name} {self.receiver_phone}"


class DeliveryStatus(Enum):
    CANCELED = "لغو شده"
    PENDING = "در انتظار تایید"
    PROCESSING = "درحال پردازش"
    SHIPPED = "ارسال شده"
    DELIVERED = "تحویل داده شده"


class PaymentStatus(Enum):
    OPEN_ORDER = "باز"
    PENDING_PAYMENT = "در انتظار پرداخت"
    PAID = "پرداخت شده"


DELIVERY_STATUS_CHOICES = [(status.name, status.value) for status in DeliveryStatus]
PAYMENT_STATUS_CHOICES = [(status.name, status.value) for status in PaymentStatus]


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='orders')

    slug = models.SlugField(max_length=6, unique=True, blank=True, null=True)  # شماره سفارش
    # Status Fields -------------- Start
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, blank=True, null=True)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS_CHOICES, blank=True, null=True)
    delivery_canceled_reason = models.CharField(max_length=155, blank=True, null=True)
    repayment_date_expire = models.DateTimeField(blank=True, null=True)
    lock_for_payment = models.BooleanField(default=False)

    # -------------- End

    coupon = models.ForeignKey(Coupon, on_delete=models.DO_NOTHING, related_name='orders', blank=True, null=True)
    shipping = models.ForeignKey(ShippingRate, on_delete=models.DO_NOTHING, related_name='orders', blank=True,
                                 null=True)
    address = models.ForeignKey(OrderAddress, on_delete=models.DO_NOTHING, related_name='orders', blank=True, null=True)

    # Fields that Fill After Payment -------------- Start

    tracking_code = models.CharField(max_length=155, blank=True, null=True)  # کد رهگیری از طرف شرکت پست

    coupon_effect_price = models.PositiveIntegerField(default=0)  # تاثیر کد تخفیف بعد خرید
    shipping_effect_price = models.IntegerField(default=0)  # هزینه ارسال بعد خرید

    date_delivery_status_updated = models.DateTimeField(blank=True, null=True)
    date_ordered = models.DateTimeField(blank=True, null=True)  # تاریخ خرید
    date_shipped = models.DateTimeField(blank=True, null=True)
    date_delivered = models.DateTimeField(blank=True, null=True)
    # -------------- End

    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)

    def get_absolute_url(self):
        return f"/panel/orders/{self.slug}"

    class Meta:
        ordering = ['-date_ordered']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_status = self.delivery_status

    def save(self, *args, **kwargs):
        if self.delivery_status != self.__original_status:
            if self.delivery_status == DeliveryStatus.PENDING.name:
                self.send_order_status_notification('tmd3150snfzkgxj')
            elif self.delivery_status == DeliveryStatus.PROCESSING.name:
                title = f'سفارش {self.slug} شما باموفقیت تایید شد'
                message = f'سفارش شما تایید و در حال پردازش می باشد همچنین شما می توانید از طریق فشردن لینک زیر جزئیات سفارش خود را مشاهده کنید'
                link = self.get_absolute_url()
                # add_notification_to_user_celery.delay(user_id=self.user.id, order_id=self.id,
                #                                       template=notificationModels.UserNotificationTemplate.ORDER.name,
                #                                       link=link,
                #                                       title=title,
                #                                       message=message)
                notificationModels.UserNotification.objects.create(user=self.user, order=self,
                                                                   template=notificationModels.UserNotificationTemplate.ORDER.name,
                                                                   title=title, message=message, link=link)
                self.send_order_status_notification('ufk0tlhnubtlsdj')

            elif self.delivery_status == DeliveryStatus.SHIPPED.name:
                title = f'سفارش {self.slug} ارسال شد'
                message = f'سفارش شما پردازش و ارسال شد لطفا پس از دریافت مرسوله دیدگاه خود را برای محصولات ثبت کنید'
                link = self.get_absolute_url()
                # add_notification_to_user_celery.delay(user_id=self.user.id, order_id=self.id,
                #                                       template=notificationModels.UserNotificationTemplate.ORDER.name,
                #                                       link=link,
                #                                       title=title,
                #                                       message=message)
                notificationModels.UserNotification.objects.create(user=self.user, order=self,
                                                                   template=notificationModels.UserNotificationTemplate.ORDER.name,
                                                                   title=title, message=message, link=link)
                self.date_shipped = timezone.now()
                self.send_order_status_notification('fnhgvsuo2fxg5vn')
            elif self.delivery_status == DeliveryStatus.DELIVERED.name:
                self.date_delivered = timezone.now()
                print('send put comment sms')

            self.date_delivery_status_updated = timezone.now()
            self.__original_status = self.delivery_status

        if not self.slug:
            self.slug = self.generate_unique_slug()

        super().save(*args, **kwargs)

    def set_repayment_expire_date(self):
        self.repayment_date_expire = timezone.now() + timedelta(hours=1)
        self.save()

    @staticmethod
    def generate_unique_slug():
        while True:
            import random
            slug = str(random.randint(1, 999999)).zfill(6)
            if not Order.objects.filter(slug=slug).exists():
                return slug

    def __str__(self):
        return f"{self.user.email} - {self.user.phone} Count : ( {self.items.count()} ) : " \
               f"( {self.get_payment_status_display()} ) : ( {self.get_delivery_status_display()} ) "

    def send_order_status_notification(self, pattern):
        # send_order_status_celery.delay(to=self.user.phone, pattern=pattern, number=self.slug,
        #                                track_code=self.tracking_code)
        send_order_status_phone(to=self.user.phone, pattern=pattern, number=self.slug, track_code=self.tracking_code)

    @staticmethod
    def is_valid_shipping_method(user_address: UserAddresses, shipping: ShippingRate):
        # Get the ShippingPrice object with the given ID
        if not user_address or not shipping:
            return False, 'آدرس و یا شیوه ارسال نا معتبر'
        if shipping.all_area:
            # Filter all ShippingPrice objects that are active and not equal to 'همه'
            other_shipping_areas = ShippingRate.objects.filter(all_area=True, is_active=True)
            if user_address and user_address.receiver_province in [shipping_area.area for shipping_area in
                                                                   other_shipping_areas]:
                # User's main address province matches an active shipping area
                message = ResponseMessage.PAYMENT_NOT_VALID_SELECTED_SHIPPING.value
                return False, message
            else:
                return True, None
        else:
            if user_address and user_address.receiver_province == shipping.area:
                # User's main address province matches the shipping area
                return True, None
            else:
                message = ResponseMessage.PAYMENT_NOT_VALID_SELECTED_SHIPPING.value
                return False, message

    @property
    def is_paid(self):
        return self.payment_status == PaymentStatus.PAID.name

    @property
    def get_payment_price(self):

        return self.get_total_price + self.shipping_effect_price

    @property
    def get_total_price(self):
        amount = 0
        if self.is_paid:
            for item in self.items.all():
                amount += item.final_price if item.final_price else 0
            if self.coupon_effect_price is not None:
                amount -= self.coupon_effect_price
        else:
            for item in self.items.all():
                amount += item.get_total_price
        return amount

    @property
    def get_total_price_before_discount(self):
        amount = 0
        for item in self.items.all():
            amount += item.final_price if item.final_price else 0
        return amount

    @property
    def get_user_total_profit(self):
        profit = 0
        profit += self.coupon_effect_price or 0
        if self.is_paid:
            for item in self.items.all():
                profit += item.final_profit * item.count if item.final_profit else 0
        return profit

    @property
    def get_user_total_profit_before_discount(self):
        profit = 0
        if self.is_paid:
            for item in self.items.all():
                profit += item.final_profit * item.count if item.final_profit else 0
        return profit


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING, related_name="baskets")
    variant = models.ForeignKey(ProductVariant, on_delete=models.DO_NOTHING, related_name="baskets")
    count = models.IntegerField(default=0)

    final_price = models.IntegerField(null=True, blank=True, editable=False)
    final_price_before_discount = models.IntegerField(null=True, blank=True, editable=False)
    final_discount = models.IntegerField(null=True, blank=True, editable=False)
    final_profit = models.IntegerField(null=True, blank=True, editable=False)

    refund = models.ForeignKey(RefundOrderItem, on_delete=models.DO_NOTHING, related_name='order_item', blank=True,
                               null=True)

    def __str__(self):
        return f"{self.order.user.email} - {self.order.user.phone} " \
               f"- {self.product.title_ir}"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    @property
    def get_total_price(self):

        return self.variant.final_price * self.count

    @property
    def get_total_price_before_discount(self):
        return self.variant.price

    @property
    def get_total_profit(self):
        if self.variant.is_special:
            return self.variant.price - self.variant.special_price
        return 0

    @property
    def get_total_discount(self):
        if self.variant.is_special:
            return self.variant.price
        return 0

    def set_final_price(self):
        self.final_price = self.get_total_price
        self.final_price_before_discount = self.get_total_price_before_discount
        self.final_discount = self.get_total_discount
        self.final_profit = self.get_total_profit
        self.save()
