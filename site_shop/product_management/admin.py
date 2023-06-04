from django.contrib import admin
from . import models

from django import forms
from mptt.forms import TreeNodeMultipleChoiceField

from ..category_management.models import Category


class ProductVisitInline(admin.TabularInline):
    model = models.ProductVisit
    readonly_fields = ('ip', 'user')
    extra = 0


class ProductVariantInLine(admin.TabularInline):
    model = models.ProductVariant
    extra = 1


class ProductPropertyInLine(admin.TabularInline):
    model = models.ProductProperty
    extra = 0


class CategoryForm(forms.ModelForm):
    category = TreeNodeMultipleChoiceField(
        queryset=Category.objects.filter(is_active=True).all(),
        required=True,
        widget=forms.SelectMultiple
    )

    class Meta:
        model = models.Product
        fields = '__all__'

class ProductAdmin(admin.ModelAdmin):
    list_filter = ['category', 'is_active']
    list_display = ['title_ir', 'is_active',
                    'visit_count']
    list_editable = ['is_active']
    search_fields = ['title_ir', 'title_en']
    inlines = [ProductVariantInLine, ProductPropertyInLine, ProductVisitInline]
    readonly_fields = ('visit_count',)
    prepopulated_fields = {'slug': ('title_en',)}
    form = CategoryForm
    def visit_count(self, obj):
        return obj.visits.count()

    visit_count.short_description = 'Visit Count'


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.VariantType)
admin.site.register(models.VariantValue)
admin.site.register(models.VariantPrefix)
admin.site.register(models.Property)
