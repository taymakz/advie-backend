from django.db import models
import datetime
from random import randint

from django.urls import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string


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
            if self.type == "PHONE":
                print(self.code)
                # SendOTP(to=self.to, code=self.code)

            if self.type == "EMAIL":
                print(self.code)
                # send_email(to=self.to, context={'code': self.code})
            return True
        return False


class VerifyNewsletterService(models.Model):
    email = models.CharField(max_length=355)
    activate_link = models.CharField(max_length=255,unique=True)

    date_expire = models.DateTimeField()
    date_created = models.DateTimeField(auto_now_add=True, editable=False)
    date_updated = models.DateTimeField(auto_now=True, editable=False)

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

    def send_activate_link(self,request):

        if not self.is_expired():
            from settings import FRONTEND_URL
            # active_link = f"{FRONTEND_URL}/verify?nl_email=${self.activate_link}"
            active_link = f"{reverse('activate_newsletter_email',args=[self.activate_link])}"

            full_link = request.build_absolute_uri(active_link)
            print(full_link)
            # send_verify_newsletter_email(to=self.email, context={'active_link': full_link})
            return True

        return False
