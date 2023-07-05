from django.contrib import admin

from . import models
admin.site.register(models.Coupon)
admin.site.register(models.CouponUsage)