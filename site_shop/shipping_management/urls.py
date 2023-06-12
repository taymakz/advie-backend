from django.urls import path
from . import views

urlpatterns = [

    path('shipping/list/', views.ShippingListAPIView.as_view(), name='get_order_shipping'),

]
