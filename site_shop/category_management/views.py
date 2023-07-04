from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_shop.category_management.models import Category
from site_shop.category_management.serializers import CategorySerializer


class CategoryListView(ListAPIView):
    queryset = Category.objects.filter(level=0,is_delete=False)
    serializer_class = CategorySerializer
    authentication_classes = []
    permission_classes = [AllowAny]
    def list(self, request, *args, **kwargs):
        try:
            categories = self.get_queryset()
            serializer = self.get_serializer(categories, many=True)
            response_data = serializer.data

            return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
