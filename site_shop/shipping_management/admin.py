from django.contrib import admin

from . import models

admin.site.register(models.ShippingRate)
admin.site.register(models.ShippingService)