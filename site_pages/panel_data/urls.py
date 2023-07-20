from django.urls import path

from . import views

urlpatterns = [
    path('data/page/panel/', views.UserPanelDataView.as_view(), name='user_panel_data'),
]
