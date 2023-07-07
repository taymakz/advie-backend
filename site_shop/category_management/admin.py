from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from . import models


class CategoryBannerInLine(admin.StackedInline):
    model = models.CategoryBanner
    extra = 0
    ordering = ['order']


class CategoryAdmin(MPTTModelAdmin):
    list_display = ['title_en', 'title_ir', 'parent', 'slug', 'is_active']
    list_editable = ['title_ir', 'parent', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('title_en',)}
    mptt_indent_field = 'title_en'
    inlines = [CategoryBannerInLine]


admin.site.register(models.Category, CategoryAdmin)
