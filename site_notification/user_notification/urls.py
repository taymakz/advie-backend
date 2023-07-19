from django.urls import path

from . import views

urlpatterns = [
    path('user/notification/list/', views.NotificationAPIListView.as_view(), name='get_order_shipping'),

]
