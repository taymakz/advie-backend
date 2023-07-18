from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.SearchProductAPIView.as_view(), name='search'),

    path('products/', views.ProductSearchView.as_view(), name='product-search'),

    path('product/<int:sku>/', views.ProductDetailAPIView.as_view(), name='product_detail'),

    path('product/user/favorite/list/', views.UserFavoriteProductListAPIView.as_view(), name='product_favorite_list'),
    path('product/user/favorite/', views.UserFavoriteProductsView.as_view(), name='product_favorite'),

    path('product/user/recent/list/', views.UserFavoriteProductListAPIView.as_view(), name='product_recent_list'),

]
