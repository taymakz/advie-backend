from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.ProductSearchView.as_view(), name='product-search'),

    path('product/<int:sku>/', views.ProductDetailAPIView.as_view(), name='product_detail'),
]
