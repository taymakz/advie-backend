import os

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from site_utils.image.get_file_ext import get_filename_ext

load_dotenv()


def upload_category_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"
    return f"images/category/{final_name}"


class Category(MPTTModel):
    image = ProcessedImageField(upload_to=upload_category_path,
                                processors=[ResizeToFill(200, 200)],
                                format='WEBP',
                                options={'quality': 90})
    title_ir = models.CharField(max_length=100, db_index=True)
    title_en = models.CharField(max_length=100, db_index=True)
    display_title = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=100, db_index=True)
    order = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class MPTTMeta:
        order_insertion_by = ['order']

    def __str__(self):
        return f"{self.title_ir}"

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ('order',)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        url_parts = [self.slug]
        current_node = self

        # Traverse up the tree until we reach the root.
        while current_node.parent is not None:
            current_node = current_node.parent
            url_parts.insert(0, current_node.slug)

        return '/search/category/' + '/'.join(url_parts) + '/'


if os.environ.get('LOCAL_STORAGE') == 'True':

    @receiver(pre_save, sender=Category)
    def delete_old_image(sender, instance, **kwargs):
        if kwargs.get('raw'):
            # Fixtures are being loaded, so skip resizing
            return
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


class CategoryBanner(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='banners')
    image = ProcessedImageField(upload_to=upload_category_path,
                                processors=[ResizeToFill(1350, 450)],
                                format='WEBP',
                                options={'quality': 90})

    image_alt = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    url = models.URLField()
    order = models.IntegerField(default=1, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"{self.title} - {self.category.title_ir}"


if os.environ.get('LOCAL_STORAGE') == 'True':
    @receiver(pre_save, sender=CategoryBanner)
    def delete_old_image(sender, instance, **kwargs):
        if kwargs.get('raw'):
            # Fixtures are being loaded, so skip resizing
            return
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
