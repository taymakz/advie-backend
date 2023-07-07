from django.contrib import admin

from . import models


class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_active']

    list_editable = ['is_active']


admin.site.register(models.ShippingRate, ShippingRateAdmin)
admin.site.register(models.ShippingService)
