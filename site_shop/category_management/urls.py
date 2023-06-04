from django.urls import path

from . import views

urlpatterns = [

    path('category/list/', views.CategoryListView.as_view(), name='category_list'),

]
