from django.db.models import Prefetch, Q
from rest_framework import status
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse, PaginationApiResponse
from site_shop.product_management.filters import ProductFilter
from site_shop.product_management.models import Product, ProductVariant, UserFavoriteProducts, ProductVisit, \
    UserRecentVisitedProduct
from site_shop.product_management.serializers import ProductDetailSerializer, ProductCardSerializer, \
    UserFavoriteProductSerializer, SearchProductSerializer
from site_utils.http_services.get_client_ip import get_client_ip


class SearchProductAPIView(ListAPIView):
    serializer_class = SearchProductSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        if len(query) < 3:  # only search if query length is more than 3 characters
            return None
        # search for products and categories that match the query
        product_query = (
                Q(title_ir__icontains=query) |
                Q(title_en__icontains=query)
        )

        products = Product.objects.filter(product_query).distinct()[:10]

        return self.serializer_class(products, many=True).data

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset:  # if query length is less than or equal to 3, return an empty response
            return BaseResponse(data={}, status=status.HTTP_204_NO_CONTENT, message=ResponseMessage.SUCCESS.value)

        return BaseResponse(data=queryset, status=status.HTTP_200_OK, message=ResponseMessage.SUCCESS.value)


class ProductSearchView(ListAPIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = ProductCardSerializer
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.filter(is_active=True))
    )
    pagination_class = PaginationApiResponse
    filterset_class = ProductFilter


class ProductDetailAPIView(RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'sku'
    lookup_url_kwarg = 'sku'

    def get(self, request, *args, **kwargs):
        try:
            product = self.get_object()
            serializer = self.get_serializer(product)
            print(self.request.user)
            print(request.user)
            # Add Product to User Recent Visits
            if self.request.user.is_authenticated:
                new_visit_product_exist = UserRecentVisitedProduct.objects.filter(product_id=product.id,
                                                                                  user_id=self.request.user.id,
                                                                                  is_delete=False).exists()
                if not new_visit_product_exist:
                    visited_products_count = UserRecentVisitedProduct.objects.filter(
                        user_id=self.request.user.id).count()
                    if visited_products_count > 10:
                        latest_user_visit = UserRecentVisitedProduct.objects.filter(user_id=self.request.user.id,

                                                                                    is_delete=False).order_by(
                            'pk').first()
                        if latest_user_visit:
                            latest_user_visit.is_delete = True
                            latest_user_visit.save()
                    UserRecentVisitedProduct.objects.create(product=product, user=self.request.user)

            # Add Product Visit
            user_ip = get_client_ip(self.request)
            user_id = self.request.user.id if self.request.user.is_authenticated else None

            ProductVisit.objects.get_or_create(
                ip=user_ip,
                user_id=user_id,
                product_id=product.id
            )
            # ---------
            response_data = serializer.data
            return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class UserRecentProductListAPIView(ListAPIView):
    serializer_class = ProductCardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        favorite_products = UserRecentVisitedProduct.objects.filter(user=user, is_delete=False).order_by('-id')
        products = [favorite.product for favorite in favorite_products]
        return products


class UserFavoriteProductListAPIView(ListAPIView):
    serializer_class = UserFavoriteProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        favorite_products = UserFavoriteProducts.objects.filter(user=user, is_delete=False).order_by('-id')
        products = [favorite.product for favorite in favorite_products]
        return products


class UserFavoriteProductsView(APIView):

    def post(self, request):

        user = request.user
        product_id = request.data.get('product_id')
        favorites_count = UserFavoriteProducts.objects.filter(user=user, is_delete=False).count()

        # check if the product is already in the favorites, remove it
        existing_favorite = UserFavoriteProducts.objects.filter(user=user, product__id=product_id,
                                                                is_delete=False).first()
        if existing_favorite:
            existing_favorite.is_delete = True
            existing_favorite.save()
            return BaseResponse(data={'color': 'sky'}, status=status.HTTP_201_CREATED,
                                message=ResponseMessage.PRODUCT_REMOVED_FROM_FAVORITE_SUCCESSFULLY.value)

        # check if user already have 20 favorites, remove the oldest one
        if favorites_count >= 20:
            oldest_favorite = UserFavoriteProducts.objects.filter(user=user).order_by('created_at').first()
            oldest_favorite.is_delete = True
            oldest_favorite.save()
        UserFavoriteProducts.objects.create(user=user, product_id=product_id, is_delete=False)

        return BaseResponse(data={'color': 'green'}, status=status.HTTP_201_CREATED,
                            message=ResponseMessage.PRODUCT_ADDED_TO_FAVORITE_SUCCESSFULLY.value)

    def delete(self, request):
        user = request.user
        product_id = request.data.get('id')
        try:
            favorite = UserFavoriteProducts.objects.filter(user=user, product_id=product_id).first()

            favorite.delete()
            return BaseResponse(status=status.HTTP_204_NO_CONTENT,
                                message=ResponseMessage.PRODUCT_REMOVED_FROM_FAVORITE_SUCCESSFULLY.value)
        except UserFavoriteProducts.DoesNotExist:
            return BaseResponse(status=status.HTTP_404_NOT_FOUND,
                                message=ResponseMessage.FAILED.value
                                )
