from django.contrib import admin

from . import models


class TransactionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_delete']

    list_editable = ['is_delete']


admin.site.register(models.Transaction, TransactionAdmin)
