from PIL import Image
from django.db import models

from django.utils.crypto import get_random_string
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill

from site_utils.image.get_file_ext import get_filename_ext
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


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
    image_alt = models.CharField(max_length=100, blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=1, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"{self.title} - {self.position}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


@receiver(post_save, sender=SiteBanner)
def resize_banner_image(sender, instance, **kwargs):
    if kwargs.get('raw'):
        # Fixtures are being loaded, so skip resizing
        return
    if instance.image:

        # Get resize dimensions
        width, height = 0, 0
        if instance.position == 'BANNER':
            width, height = 450, 225
        elif instance.position == 'SLIDER':
            width, height = 900, 450

        # Resize and save image
        image = Image.open(instance.image.path)
        image = image.resize((width, height))
        image.save(instance.image.path)


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
