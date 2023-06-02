
from django.urls import path, include

urlpatterns = [

    # Users Section
    path('', include('site_account.user_management.urls')),
    # path('', include('site_account.user_addresses.urls')),

    # Settings Section
    # path('', include('site_setting.website_management.urls')),
    # path('', include('site_setting.website_banner.urls')),


]