from django.db import models
import datetime
from random import randint
from django.utils import timezone


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
    expire_date = models.DateTimeField()

    def __str__(self):
        return f"{self.to} : {self.code}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.code = randint(10000, 99999)
            self.expire_date = timezone.now() + datetime.timedelta(seconds=240)
        super().save(*args, **kwargs)

    def is_expired(self):
        now_utc = timezone.now()
        return self.expire_date < now_utc

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
