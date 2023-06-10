from django.db import models
from django.utils.crypto import get_random_string
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from site_utils.image.get_file_ext import get_filename_ext
from site_utils.persian.province import province


def upload_shipping_method_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"
    return f"images/coupon/{final_name}"


class ShippingMethod(models.Model):
    image = ProcessedImageField(upload_to=upload_shipping_method_image_path,
                                processors=[ResizeToFill(160, 160)],
                                format='WEBP',
                                options={'quality': 90})
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class ShippingPrice(models.Model):
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    area = models.CharField(max_length=20, choices=province, null=True, blank=True)
    all_area = models.BooleanField(default=True)
    pay_at_destination = models.BooleanField(default=False)
    price = models.PositiveIntegerField(null=True, blank=True, default=0)
    free_shipping_threshold = models.PositiveIntegerField(null=True, blank=True, default=0)
    order = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('order',)
        unique_together = ("shipping_method", "area")

    def calculate_price(self, order_price):
        # price calculation logic here
        if self.pay_at_destination:
            return 0
        elif self.free_shipping_threshold and order_price >= self.free_shipping_threshold:
            return 0
        else:
            return self.price

    def save(self, *args, **kwargs):
        if self.free_shipping_threshold and self.price is None:
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.shipping_method.name} ( {self.area} ): {self.price:,} - رایگان بالای : {self.free_shipping_threshold:,}"
