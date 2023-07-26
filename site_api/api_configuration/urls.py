from django.urls import path, include

urlpatterns = [

    # Pages Section
    path('', include('site_pages.home_data.urls')),
    path('', include('site_pages.panel_data.urls')),

    # Users Section
    path('user/', include('site_account.user_management.urls')),
    path('user/', include('site_account.user_addresses.urls')),

    # Notification Section
    path('', include('site_notification.announcement_notification.urls')),
    path('', include('site_notification.verification_notification.urls')),
    path('', include('site_notification.user_notification.urls')),

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
