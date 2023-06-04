
from django.urls import path, include

urlpatterns = [

    # Pages Section
    path('', include('site_pages.home_data.urls')),

    # Users Section
    path('', include('site_account.user_management.urls')),
    # path('', include('site_account.user_addresses.urls')),

    # Settings Section
    # path('', include('site_setting.website_management.urls')),
    # path('', include('site_setting.website_banner.urls')),

    # Shop Section

    # Category Section
    path('', include('site_shop.category_management.urls')),

]