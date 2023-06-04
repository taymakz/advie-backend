from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from api_configuration.enums import ResponseMessage
from api_configuration.response import BaseResponse
from site_shop.product_management.models import Product
from site_shop.product_management.serializers import ProductCardSerializer


# class ProductListAPIView(ListAPIView):
#     authentication_classes = []
#     permission_classes = [AllowAny]
#     queryset = Product.objects.filter(is_active=True).all()
#     serializer_class = ProductCardSerializer
#
#     def list(self, request, *args, **kwargs):
#         try:
#             products = self.get_queryset()
#             serializer = self.get_serializer(products, many=True)
#             response_data = serializer.data
#             return BaseResponse(data=response_data, status=status.HTTP_200_OK,
#                                 message=ResponseMessage.SUCCESS.value)
#
#         except:
#             return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
#                                 message=ResponseMessage.FAILED.value)
