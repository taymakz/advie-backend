from django.contrib import admin

from . import models


class CouponAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_delete']

    list_editable = ['is_delete']


admin.site.register(models.Coupon, CouponAdmin)
admin.site.register(models.CouponUsage)
