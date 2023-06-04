from random import randint

from ckeditor_uploader.fields import RichTextUploadingField
from django.core.cache import cache
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.text import slugify
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from site_account.user_management.models import User
from site_shop.category_management.models import Category
from site_utils.image.get_file_ext import get_filename_ext


def upload_product_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"

    return f"images/product/{final_name}"


class VariantType(models.Model):
    title_ir = models.CharField(max_length=100)
    title_en = models.CharField(max_length=100)
    SELECT_STYLE = (
        ('RADIO', 'RADIO'),
        ('DROP_DOWN', 'DROP_DOWN'),
    )
    select_style = models.CharField(max_length=20, choices=SELECT_STYLE, default="RADIO")
    is_none = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title_ir} - {self.title_en}"


class Product(models.Model):
    image = ProcessedImageField(upload_to=upload_product_path,
                                default='images/products/default_product.png',
                                processors=[ResizeToFill(400, 400)],
                                format='WEBP',
                                options={'quality': 90})
    title_ir = models.CharField(max_length=255)
    title_en = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, db_index=True, unique=True, null=True, blank=True)
    sku = models.IntegerField(blank=True, db_index=True, null=True, unique=True, editable=False)
    description = RichTextUploadingField(blank=True, null=True)
    variant_type = models.ForeignKey(VariantType, on_delete=models.DO_NOTHING, related_name="products")
    category = models.ManyToManyField(Category, related_name='products', db_index=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    @property
    def is_available_in_stock(self):
        for variant in self.variants.filter(is_active=True):
            if variant.stock > 0:
                return True
        return False

    @property
    def has_special_price(self):
        for variant in self.variants.all():
            if (variant.special_price or 0) > 0:
                return True
        return False

    def get_variants(self):
        return self.variants.all()

    def get_absolute_url(self):
        return f"/product/{self.sku}/{self.slug}/"

    @property
    def visit_count(self):
        cache_key = f'product_visit_count_{self.pk}'
        visit_count = cache.get(cache_key)
        if visit_count is None:
            visit_count = self.visits.count()
            cache.set(cache_key, visit_count)
        return visit_count

    def minimum_variant(self):
        return self.variants.filter(is_active=True).order_by('price').first()

    @property
    def minimum_variant_price(self):
        variant = self.minimum_variant()
        return variant.price if variant else 0

    @property
    def minimum_variant_special_price(self):
        variant = self.minimum_variant()
        return variant.special_price if variant else None

    @property
    def minimum_variant_special_price_percent(self):
        variant = self.minimum_variant()
        if variant:
            return int((variant.price - variant.special_price) / variant.price * 100) if variant.special_price else None
        else:
            return None

    @property
    def minimum_variant_is_special(self):
        variant = self.minimum_variant()
        return variant.is_special if variant else False

    @property
    def minimum_variant_final_price(self):
        variant = self.minimum_variant()
        return variant.final_price if variant else 0

    def save(self, *args, **kwargs):
        if self.sku is None:
            sku = randint(10000, 99999)
            while Product.objects.filter(sku=sku).exists():
                sku = randint(10000, 99999)
            self.sku = sku

        self.slug = slugify(self.title_en)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title_ir


@receiver(pre_save, sender=Product)
def delete_old_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_object = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return

    new_image = instance.image
    old_image = old_object.image

    if new_image != old_image:
        # Delete the old image from storage
        old_object.image.delete(save=False)


class VariantPrefix(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class VariantValue(models.Model):
    type = models.ForeignKey(VariantType, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)
    prefix = models.ForeignKey(VariantPrefix, on_delete=models.CASCADE)

    color_code = models.CharField(max_length=100, null=True, blank=True, verbose_name="Color (Not Required)")

    def __str__(self):
        return f"{self.value} - {self.prefix}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    type = models.ForeignKey(VariantType, on_delete=models.CASCADE, null=True, blank=True, related_name='variants')
    value = models.ForeignKey(VariantValue, on_delete=models.CASCADE, null=True, blank=True)
    price = models.PositiveIntegerField(default=0)
    special_price = models.PositiveIntegerField(null=True, blank=True)
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    @property
    def special_price_percent(self):
        if self.price and self.special_price:
            return int((self.price - self.special_price) / self.price * 100)
        else:
            return None

    @property
    def is_special(self):
        if (self.special_price or 0) > 0:
            return True
        return False

    @property
    def final_price(self):
        if self.special_price is not None:
            return self.special_price
        else:
            return self.price

    def __str__(self):
        return self.product.title_ir


class ProductVisit(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='visits')
    ip = models.CharField(max_length=30, verbose_name='user ip')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.title_en} / {self.ip}'

    class Meta:
        verbose_name = 'product visit'
        verbose_name_plural = 'product visits'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache_key = f'product_visit_count_{self.product.pk}'
        cache.incr(cache_key)


class Property(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ProductProperty(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='properties')
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.property.name


# class ProductComment(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     comment = models.TextField()
#     SUGGEST_CHOICE = (
#         ('y', 'پیشنهاد میکنم'),
#         ('n', 'پیشنهاد نمی کنم'),
#     )
#     suggest = models.CharField(max_length=1, choices=SUGGEST_CHOICE)
#     score = models.CharField(max_length=10)
#     create_date = models.DateTimeField(auto_now_add=True)
#     accept_by_admin = models.BooleanField(default=False)
#
#     def __str__(self):
#         return f"{self.user} on {self.product.title_en} score : {self.score} suggest : {self.get_suggest_display()} : {self.comment[:50]}"


class UserFavoriteProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class UserRecentVisitedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recent_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} {self.product.title_ir}"
