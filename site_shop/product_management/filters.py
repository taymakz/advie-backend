import django_filters
from django.db.models import Q, Max, Min, Sum, Count, Case, When, IntegerField, F
from django.utils import timezone

from site_account.user_management.models import UserSearchHistory
from .models import Product
from ..category_management.models import Category


class ProductFilter(django_filters.FilterSet):
    categorySlug = django_filters.CharFilter(method='filter_category')
    subCategorySlug = django_filters.CharFilter(method='filter_sub_category')
    search = django_filters.CharFilter(method='filter_search')
    available = django_filters.BooleanFilter(method='filter_available')
    special = django_filters.BooleanFilter(method='filter_special')
    sort = django_filters.CharFilter(method='filter_sort')

    def filter_search(self, queryset, name, value):
        if value:
            user = self.request.user  # Get the current user
            if user.is_authenticated:
                # Create a new search history instance for the user
                UserSearchHistory.objects.create(user=user, search=value)

                # Limit the user's search history to a maximum of 20 records
                # Delete the oldest records if the limit is exceeded
                search_history_count = UserSearchHistory.objects.filter(user=user).count()
                if search_history_count > 20:
                    oldest_searches = UserSearchHistory.objects.filter(user=user).order_by('created_at')[
                                      :search_history_count - 20]
                    oldest_searches.delete()

            return queryset.filter(
                Q(title_ir__icontains=value) |
                Q(title_en__icontains=value) |
                Q(description__icontains=value)
            )
        return queryset

    def filter_special(self, queryset, name, value):

        if value:
            return queryset.filter(
                is_active=True,
                variants__is_active=True,
                variants__special_price__isnull=False,
                variants__special_price_start_date__lte=timezone.now(),
                variants__special_price_end_date__gte=timezone.now()
            ).distinct()
        return queryset

    def filter_available(self, queryset, name, value):

        if value:
            return queryset.filter(variants__is_active=True, variants__stock__gt=0).distinct()
        return queryset

    def filter_sort(self, queryset, name, value):
        if value in ['1', '2', '3', '4']:
            if value == '1':
                queryset.order_by('-date_created')
            elif value == '2':
                queryset.annotate(
                    order_count=Sum(
                        'baskets__count'
                    )).order_by('-order_count', '-date_created')
            elif value == '3':
                queryset.annotate(highest_price=Max('variants__price')).order_by('-highest_price')
            elif value == '4':
                queryset.annotate(lowest_price=Min('variants__price')).order_by('lowest_price')

            return queryset.annotate(
                variants_count=Count(
                    'variants__stock',
                    filter=Q(variants__is_active=True)
                )
            ).order_by(
                '-variants_count',
                Case(
                    When(variants_count=0, then=F('id')),
                    default=0,
                    output_field=IntegerField()
                )
            )

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
