from django.contrib import admin

from . import models


class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'template', 'is_read', 'is_delete']
    list_editable = ['is_read', 'is_delete']


admin.site.register(models.UserNotification, UserNotificationAdmin)
