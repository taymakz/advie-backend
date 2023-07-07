import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from site_utils.image.get_file_ext import get_filename_ext


class UserManager(BaseUserManager):
    def create_user(self, email=None, phone=None, password=None, **extra_fields):
        if email:
            email = self.normalize_email(email)
        phone = phone or None  # set default value if phone is not provided
        user = self.model(email=email, phone=phone, **extra_fields)

        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, phone=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if not email and not phone:
            raise ValueError('At least one of email or phone must be set')
        user = self.create_user(email=email, phone=phone, password=password, **extra_fields)
        user.save(using=self._db)
        return user


def upload_profile_path(instance, filename):
    name, ext = get_filename_ext(filename)
    final_name = f"{get_random_string(30)}{ext}"
    return f"images/profile/{final_name}"


class User(AbstractUser):
    username = models.IntegerField(null=True, blank=True)
    profile = ProcessedImageField(upload_to=upload_profile_path,
                                  default='images/profile/default_profile.png',
                                  processors=[ResizeToFill(100, 100)],
                                  format='WEBP',
                                  options={'quality': 90})

    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=11, blank=True, null=True, unique=True)
    national_code = models.CharField(max_length=10, null=True, blank=True)
    verified = models.BooleanField(default=False)
    forgot_password_token = models.UUIDField(null=True, blank=True)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    objects = UserManager()

    is_delete = models.BooleanField(default=False)

    def generate_forgot_password_token(self):
        self.forgot_password_token = uuid.uuid4()
        self.save()

    def revoke_all_tokens(self):
        for token in OutstandingToken.objects.filter(user=self).exclude(
                id__in=BlacklistedToken.objects.filter(token__user=self).values_list('token_id', flat=True),
        ):
            BlacklistedToken.objects.create(token=token)

    def is_verify(self):
        return self.verified

    def __str__(self):
        return f"{self.username}"


# if os.environ.get('LOCAL_STORAGE') == 'True':
@receiver(pre_save, sender=User)
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

    new_image = instance.profile
    old_image = old_object.profile

    if new_image != old_image:
        # Delete the old image from storage
        old_object.profile.delete(save=False)


class UserSearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="search_history")
    search = models.CharField(max_length=200)
