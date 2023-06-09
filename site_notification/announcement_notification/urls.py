from django.urls import path
from . import views

urlpatterns = [

    path('newsletter/submit/', views.NewsletterCreateView.as_view()),

]
