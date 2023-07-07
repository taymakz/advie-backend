from django import forms
from django.contrib import admin
from django.utils.html import format_html

from . import models


class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
            'profile', 'email', 'phone', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_delete',
            'national_code', 'last_login')


class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = (
        'profile_image', 'email', 'phone', 'first_name', 'last_name', 'is_superuser', 'is_delete',)

    def profile_image(self, obj):
        if obj.profile:
            return format_html(f'<img src="{obj.profile.url}" width="50px" />')
        else:
            return ''


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserSearchHistory)
