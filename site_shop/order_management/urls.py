from django.urls import path
from . import views

urlpatterns = [

    path('order/list/', views.UserPaidOrderListAPIView.as_view(), name='get_user_paid_order_list'),
    path('order/<int:id>/', views.UserPaidOrderDetailAPIView.as_view(), name='get_user_paid_order_detail'),

    path('order/current/', views.GetUserCurrentOrderView.as_view(), name='get_user_current_order'),
    path('order/current/add/', views.AddItemToCurrentOrderView.as_view(), name='add_item_to_user_current_order'),

    path('order/current/item/count/increase/', views.IncreaseCurrentOrderItemCountView.as_view(),
         name='increase_user_order_item_count'),
    path('order/current/item/count/decrease/', views.DecreaseCurrentOrderItemCountView.as_view(),
         name='decrease_user_order_item_count'),
    path('order/current/item/remove/', views.RemoveCurrentOrderItemView.as_view(), name='remove_user_order_item'),

]
