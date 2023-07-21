import datetime
from random import randint

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string

from site_notification.verification_notification.tasks import send_otp_celery


class VerifyOTPService(models.Model):
    TYPE_OPTIONS = (
        ('PHONE', 'تلفن'),
        ('EMAIL', 'ایمیل')
    )
    USAGE_OPTIONS = (
        ('AUTHENTICATE', 'احراز هویت'),
        ('RESET_PASSWORD', 'بازیابی کلمه عبور'),
        ('VERIFY', 'تایید')
    )

    type = models.CharField(max_length=5, choices=TYPE_OPTIONS)
    usage = models.CharField(max_length=14, choices=USAGE_OPTIONS, default='AUTHENTICATE')
    to = models.CharField(max_length=355)
    code = models.CharField(max_length=5)
    date_expire = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.to} : {self.code}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = randint(10000, 99999)
            self.date_expire = timezone.now() + datetime.timedelta(seconds=240)
        super().save(*args, **kwargs)

    def is_expired(self):
        now_utc = timezone.now()
        return self.date_expire < now_utc

    def send_otp(self):

        if not self.is_expired():
            send_otp_celery.delay(to=self.to, code=self.code, type=self.type)
            # if self.type == 'PHONE':
            #     send_otp_phone(to=self.to, code=self.code)
            # else:
            #     send_otp_email(to=self.to, context={'code': self.code})


class VerifyNewsletterService(models.Model):
    email = models.CharField(max_length=355)
    activate_link = models.CharField(max_length=255, unique=True)

    date_expire = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} : {self.activate_link}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.activate_link = get_random_string(255)
            self.date_expire = timezone.now() + datetime.timedelta(days=7)
        super().save(*args, **kwargs)

    def is_expired(self):
        now_utc = timezone.now()
        return self.date_expire < now_utc

    def send_activate_link(self, request):

        if not self.is_expired():
            active_link = f"{reverse('activate_newsletter_email', args=[self.activate_link])}"
            # todo
            full_link = request.build_absolute_uri(active_link)
            print(full_link)
            # send_verify_newsletter_email(to=self.email, context={'active_link': full_link})
            return True

        return False
