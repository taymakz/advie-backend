from django.contrib import admin
from . import models

class OrderAdmin(admin.ModelAdmin):
    # inlines = [OrderAddressInline]
    readonly_fields = ('coupon_effect_price','shipping_effect_price')
    list_display = ['__str__', 'is_delete']

    list_editable = ['is_delete']

class OrderItemAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'is_delete']

    list_editable = ['is_delete']
class OrderAddressAdmin(admin.ModelAdmin):

    list_display = ['__str__', 'is_delete']

    list_editable = ['is_delete']


admin.site.register(models.Order, OrderAdmin)
admin.site.register(models.OrderItem,OrderItemAdmin)
admin.site.register(models.OrderAddress,OrderAddressAdmin)