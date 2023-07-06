import time

from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_setting.website_banner.models import SiteBanner
from site_setting.website_banner.serializers import SiteBannerSerializer
from site_shop.product_management.models import Product
from site_shop.product_management.serializers import ProductCardSerializer


class HomeDataView(generics.ListAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = SiteBannerSerializer

    def get(self, request, *args, **kwargs):
        # Get active banners
        banners = SiteBanner.objects.filter(is_active=True, is_delete=False)
        banner_serializer = self.get_serializer(banners, many=True)

        # Get most sale products
        most_sale_products = Product.objects.filter(is_active=True, is_delete=False, variants__stock__gt=0,
                                                    variants__is_active=True, variants__is_delete=False).order_by(
            '-date_created')[:10]
        most_sale_products_serializer = ProductCardSerializer(most_sale_products, many=True)

        # Get latest products
        latest_products = Product.objects.filter(is_active=True, is_delete=False, variants__stock__gt=0,
                                                 variants__is_active=True, variants__is_delete=False).order_by(
            '-date_created')[:10]
        latest_products_serializer = ProductCardSerializer(latest_products, many=True)

        # Return the data as JSON

        response_data = {
            'banners': banner_serializer.data,
            'special_sale_products': latest_products_serializer.data,
            'latest_products': latest_products_serializer.data,
            'best_selling_products': latest_products_serializer.data,
        }
        return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                            message=ResponseMessage.SUCCESS.value)
