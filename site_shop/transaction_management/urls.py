from django.urls import path

from . import views

urlpatterns = [
    path('payment/request/check/', views.RequestPaymentCheckAPIView.as_view(), name='check_payment'),
    path('payment/request/submit/', views.RequestPaymentSubmitAPIView.as_view(), name='submit_payment'),

    path('payment/request/submit/pending/', views.RequestRePaymentSubmitAPIView.as_view(),
         name='submit_re_payment'),

    path('payment/verify/', views.VerifyPaymentAPIView.as_view(), name='verify_payment'),

    path('checkout/result/<str:transaction_id>/<str:transaction_slug>/', views.CheckoutResultAPIView.as_view(),
         name='checkout_result')

]
