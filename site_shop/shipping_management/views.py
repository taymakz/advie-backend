from django.shortcuts import render
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_shop.shipping_management.models import ShippingRate
from site_shop.shipping_management.serializers import ShippingRateSerializer


class ShippingListAPIView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ShippingRate.objects.filter(is_active=True).all()
    serializer_class = ShippingRateSerializer
    pagination_class = []
    def list(self, request, *args, **kwargs):
        try:
            shipping_rates = self.get_queryset()
            serializer = self.get_serializer(shipping_rates, many=True)
            response_data = serializer.data

            return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
