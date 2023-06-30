from django.urls import path
from . import views

urlpatterns = [
    path('address/', views.AddressListCreateUpdateDestroyAPIView.as_view(), name='current_user_address'),
    path('address/get/<int:pk>/', views.GetAddressByIdView.as_view(), name='current_user_address_get_by_id'),

]
