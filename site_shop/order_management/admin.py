from django.contrib import admin
from . import models
class OrderAdmin(admin.ModelAdmin):
    # inlines = [OrderAddressInline]
    readonly_fields = ('coupon_effect_price','shipping_effect_price')


admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem)
admin.site.register(models.OrderAddress)