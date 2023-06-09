import django_filters
from .models import Product
from django.db.models import Q, Max, Min

from ..category_management.models import Category
from django.utils import timezone


class ProductFilter(django_filters.FilterSet):
    categorySlug = django_filters.CharFilter(method='filter_category')
    subCategorySlug = django_filters.CharFilter(method='filter_sub_category')
    search = django_filters.CharFilter(method='filter_search')
    available = django_filters.BooleanFilter(method='filter_available')
    special = django_filters.BooleanFilter(method='filter_special')
    sort = django_filters.CharFilter(method='filter_sort')

    def filter_search(self, queryset, name, value):
        if value:

            return queryset.filter(
                Q(title_ir__icontains=value) |
                Q(title_en__icontains=value) |
                Q(another_field__icontains=value)
            )
        return queryset

    def filter_special(self, queryset, name, value):

        if value:
            return queryset.filter(variants__special_price__isnull=False,
                                   variants__special_price_start_date__lte=timezone.now(),
                                   variants__special_price_end_date__gte=timezone.now()
                                   ).distinct()
        return queryset
    def filter_available(self, queryset, name, value):

        if value:
            return queryset.filter(variants__is_active=True, variants__stock__gt=0).distinct()
        return queryset
    def filter_sort(self, queryset, name, value):
        if value:
            if value == '1':
                return queryset.order_by('-date_created')
            elif value == '2':
                return queryset.order_by('-date_created')
            elif value == '3':
                return queryset.annotate(highest_price=Max('variants__price')).order_by('-highest_price')
            elif value == '4':
                return queryset.annotate(lowest_price=Min('variants__price')).order_by('lowest_price')

        return queryset
    def filter_category(self, queryset, name, value):
        if value:
            category = Category.objects.get(slug=value)
            queryset = queryset.filter(category__in=category.get_descendants(include_self=True)).distinct()
            # if not self.request.query_params.get('subCategorySlug'):
            #     queryset = queryset.distinct()  # Exclude duplicates when subCategorySlug is not specified
        return queryset

    def filter_sub_category(self, queryset, name, value):
        if value:
            sub_category = Category.objects.get(slug=value)
            queryset = queryset.filter(category=sub_category).distinct()
            # if not self.request.query_params.get('categorySlug'):
            #     queryset = queryset.distinct()  # Exclude duplicates when categorySlug is not specified
        return queryset

    class Meta:
        model = Product
        fields = ['search']
