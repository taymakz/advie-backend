from django.urls import path, include
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    # Pages Section
    path('', include('site_pages.home_data.urls')),

    # Users Section
    path('user/', include('site_account.user_management.urls')),
    path('user/', include('site_account.user_addresses.urls')),

    # Notification Section
    path('', include('site_notification.announcement_notification.urls')),
    path('', include('site_notification.verification_notification.urls')),

    # Settings Section
    # path('', include('site_setting.website_management.urls')),
    # path('', include('site_setting.website_banner.urls')),

    # Shop Section
    # Payment Section
    path('', include('site_shop.transaction_management.urls')),


    # Category Section
    path('', include('site_shop.category_management.urls')),

    # Product Section
    path('', include('site_shop.product_management.urls')),

    # Order Section
    path('', include('site_shop.order_management.urls')),

    # Shipping Section
    path('', include('site_shop.shipping_management.urls')),

    # Coupon Section
    path('', include('site_shop.coupon_management.urls')),


]
