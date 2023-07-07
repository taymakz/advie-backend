from django.contrib import admin

from . import models

admin.site.register(models.VerifyOTPService)
admin.site.register(models.VerifyNewsletterService)
