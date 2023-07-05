from django.urls import path
from . import views

urlpatterns = [

    path('coupon/use/', views.UseCouponCodeAPIView.as_view(), name='use_coupon'),

]
