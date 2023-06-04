from django.urls import path
from . import views

urlpatterns = [
    path('data/page/home/', views.HomeDataView.as_view(), name='home_data'),
]
