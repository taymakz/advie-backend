from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from jalali_date import date2jalali

from site_account.user_management.models import User

from site_utils.image.get_file_ext import get_filename_ext


def upload_coupon_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(20)}{instance}{ext}"
    return f"images/coupon/{final_name}"


class Coupon(models.Model):
    image = models.ImageField(upload_to=upload_coupon_image_path, null=True, blank=True)
    title = models.CharField(max_length=155, null=True, blank=True)
    pin = models.BooleanField(default=False)
    code = models.CharField(max_length=50, unique=True, validators=[
        RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed.')
    ])
    discount_type = models.CharField(max_length=1, choices=[('%', 'Percentage'), ('$', 'Fixed amount')])

    discount_amount = models.PositiveIntegerField(validators=[
        MinValueValidator(0)
    ])
    max_usage = models.PositiveIntegerField(blank=True, null=True, validators=[
        MinValueValidator(1),
    ])
    max_usage_per_user = models.PositiveIntegerField(blank=True, null=True, validators=[
        MinValueValidator(1),
    ])
    usage_count = models.PositiveIntegerField(default=0, validators=[
        MinValueValidator(0)
    ])
    min_order_total = models.PositiveIntegerField(blank=True, null=True, validators=[
        MinValueValidator(0)
    ])
    max_order_total = models.PositiveIntegerField(blank=True, null=True, validators=[
        MinValueValidator(0)
    ])
    only_first_order = models.BooleanField(default=False)
    date_start = models.DateTimeField()
    date_expire = models.DateTimeField()
    
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return f"[ {self.code} ] {self.discount_amount:,}{self.discount_type} (usage : {self.usage_count})"

    class Meta:
        ordering = ('-date_created',)

    def calculate_discount(self, price):
        if self.discount_type == '%':
            discount = int(round(price * (self.discount_amount / 100)))
        else:
            discount = int(min(self.discount_amount, price))

        discounted_price = int(price - discount)
        discount_difference = int(price - discounted_price)
        return discounted_price, discount_difference

    def clean(self):
        super().clean()
        if self.max_usage and self.usage_count > self.max_usage:
            raise ValidationError('Max user usage cannot be greater than max usage.')
        if self.min_order_total is not None and self.max_order_total is not None and self.min_order_total > self.max_order_total:
            raise ValidationError('Minimum order total cannot be greater than maximum order total.')
        if self.date_expire <= self.date_start:
            raise ValidationError('expire date must be after start date.')

    def validate_coupon(self, order_total_price, user_id):
        if self.max_usage is not None and self.max_usage <= self.usage_count:
            return False, 'کد تخفیف به حداکثر حد مجاز استفاده رسیده است'
        if self.max_usage_per_user is not None:
            user = User.objects.filter(id=user_id).first()
            coupon_usage = CouponUsage.objects.filter(coupon=self, user=user).first()
            if coupon_usage is not None and coupon_usage.usage_count >= self.max_usage_per_user:
                return False, f'کد تخفیف وارد شده فقط {self.max_usage_per_user} بار  قابل استفاده برای هر کاربری میباشد'
        if self.date_expire is not None and self.date_expire <= timezone.now():
            return False, 'کد تخفیف دیگر معتبر نمیباشد'
        if self.min_order_total is not None and order_total_price < self.min_order_total:
            return False, f'کد تخفیف وارد شده قابل استفاده برای سفارش های بیشتر از {self.min_order_total:,} می باشد'
        if self.max_order_total is not None and order_total_price > self.max_order_total:
            return False, f'کد تخفیف وارد شده قابل استفاده برای سفارش های کمتر از {self.max_order_total:,} می یباشد'
        if timezone.now() < self.date_start:
            time = date2jalali(self.date_start)
            return False, f'کد تخفیف وارد شده از تاریخ {time} قابل استفاده می باشد'
        if timezone.now() > self.date_expire:
            return False, f'کد تخفیف وارد شده منقضی شده است'

        if self.only_first_order:
            from site_shop.order_management.models import Order
            if Order.objects.filter(user_id=user_id).exists():
                return False, 'کد تخفیف فقط برای اولین خرید کاربر قابل استفاده است'

        return True, 'کد تخفیف با موفقیت اعمال شد'


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    usage_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('coupon', 'user')
