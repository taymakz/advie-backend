from django.contrib import admin
from django import forms
from . import models
from django.utils.html import format_html



class UserForm(forms.ModelForm):
    class Meta:
        model = models.User
        fields = (
        'profile', 'username', 'email', 'phone', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active',
        'national_code','last_login','password')


class UserAdmin(admin.ModelAdmin):
    form = UserForm
    list_display = (
    'profile_image', 'username', 'email', 'phone', 'first_name', 'last_name', 'is_superuser', 'is_active',)

    def profile_image(self, obj):
        if obj.profile:
            return format_html(f'<img src="{obj.profile.url}" width="50px" />')
        else:
            return ''


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserSearchHistory)

