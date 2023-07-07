import os

from PIL import Image
from django.core.files.storage import default_storage
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from dotenv import load_dotenv
from imagekit.models import ProcessedImageField

from site_utils.image.get_file_ext import get_filename_ext

load_dotenv()


def upload_banner_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"
    return f"images/banner/{final_name}"


class SiteBanner(models.Model):
    CHOICE_POSITION = (
        ('SLIDER', 'SLIDER'),
        ('BANNER', 'BANNER'),
    )
    position = models.CharField(choices=CHOICE_POSITION, max_length=6)
    title = models.CharField(max_length=100)
    image = ProcessedImageField(upload_to=upload_banner_path,
                                format='WEBP',
                                options={'quality': 90})
    resize_width = models.PositiveIntegerField(default=0)
    resize_height = models.PositiveIntegerField(default=0)
    image_alt = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"{self.title} - {self.position} {self.resize_width}x{self.resize_height}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


if os.environ.get('LOCAL_STORAGE') == 'True':

    @receiver(post_save, sender=SiteBanner)
    def resize_banner_image(sender, instance, **kwargs):
        if kwargs.get('raw'):
            # Fixtures are being loaded, so skip resizing
            return
        if instance.image:
            # Get resize dimensions
            width, height = instance.resize_width, instance.resize_height

            # Resize and save image
            image = Image.open(instance.image.path)
            image = image.resize((width, height))
            image.save(instance.image.path)
else:
    @receiver(post_save, sender=SiteBanner)
    def resize_banner_image(sender, instance, **kwargs):
        if kwargs.get('raw'):
            # Fixtures are being loaded, so skip resizing
            return
        if instance.image:
            # Get resize dimensions
            width, height = instance.resize_width, instance.resize_height

            # Open the image using storage API
            with default_storage.open(instance.image.name, 'rb') as file:
                image = Image.open(file)

                # Resize and save the image
                resized_image = image.resize((width, height))

                with default_storage.open(instance.image.name, 'wb') as resized_file:
                    resized_image.save(resized_file)


@receiver(pre_save, sender=SiteBanner)
def delete_old_image(sender, instance, **kwargs):
    if kwargs.get('raw'):
        # Fixtures are being loaded, so skip deleting old image
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
