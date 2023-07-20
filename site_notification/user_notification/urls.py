from django.urls import path

from . import views

urlpatterns = [
    path('user/notification/list/', views.NotificationAPIListView.as_view(), name='get_user_notifications'),
    path('user/notification/remove/', views.RemoveAllNotificationAPIView.as_view(), name='remove_user_notifications'),

]
