from django.db import models
from django.utils.crypto import get_random_string
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from site_utils.image.get_file_ext import get_filename_ext
from site_utils.persian.province import province


def upload_shipping_method_image_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"
    return f"images/shipping-service/{final_name}"


class ShippingService(models.Model):
    image = ProcessedImageField(upload_to=upload_shipping_method_image_path,
                                processors=[ResizeToFill(160, 160)],
                                format='PNG',
                                options={'quality': 90})
    name = models.CharField(max_length=100)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name}"


class ShippingRate(models.Model):
    shipping_service = models.ForeignKey(ShippingService, on_delete=models.CASCADE)
    area = models.CharField(max_length=20, choices=province, null=True, blank=True)
    all_area = models.BooleanField(default=False)
    pay_at_destination = models.BooleanField(default=False)
    price = models.PositiveIntegerField(null=True, blank=True, default=0)
    free_shipping_threshold = models.PositiveIntegerField(null=True, blank=True, default=0)
    order = models.IntegerField(default=1, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        ordering = ('order',)
        unique_together = [("shipping_service", "area"),("shipping_service", "all_area")]


    def calculate_price(self, order_price):
        if self.pay_at_destination or order_price < self.free_shipping_threshold:
            return 0
        else:
            return self.price

    def save(self, *args, **kwargs):
        if self.free_shipping_threshold and self.price is None:
            self.price = 0
        super().save(*args, **kwargs)

    def __str__(self):

        return f"{self.shipping_service.name} ( {self.area} ): {self.price:,} " \
               f"- رایگان بالای : {self.free_shipping_threshold:,}"
