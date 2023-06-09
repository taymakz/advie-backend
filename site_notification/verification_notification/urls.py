from django.urls import path
from . import views

urlpatterns = [

    path('verify/nl/em/<str:activate_link>', views.ActivateNewsletterEmail.as_view(), name="activate_newsletter_email")
]
