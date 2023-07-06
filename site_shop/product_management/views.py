from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse, PaginationApiResponse
from site_shop.product_management.filters import ProductFilter
from site_shop.product_management.models import Product, ProductVariant
from site_shop.product_management.serializers import ProductDetailSerializer,ProductCardSerializer
from django.db.models import Prefetch


class ProductSearchView(ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    serializer_class = ProductCardSerializer
    queryset = Product.objects.filter(is_active=True, is_delete=False).prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.filter(is_active=True, is_delete=False))
    )
    pagination_class = PaginationApiResponse
    filterset_class = ProductFilter



class ProductDetailAPIView(RetrieveAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True,is_delete=False)
    serializer_class = ProductDetailSerializer
    lookup_field = 'sku'
    lookup_url_kwarg = 'sku'

    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            response_data = serializer.data
            return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
