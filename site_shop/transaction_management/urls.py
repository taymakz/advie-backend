from django.urls import path
from . import views

urlpatterns = [
    path('payment/request/check/', views.RequestPaymentCheckAPIView.as_view(), name='check_payment'),
    # path('payment/request/submit/', views.RequestPaymentAPIView.as_view(), name='submit_payment'),
    path('payment/verify/', views.VerifyPaymentAPIView.as_view(), name='verify_payment')
]
