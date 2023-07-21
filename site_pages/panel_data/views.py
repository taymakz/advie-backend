from django.db.models import Count
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_shop.order_management.models import Order, DeliveryStatus, OrderItem
from site_shop.product_management.models import UserFavoriteProducts
from site_shop.refund_management.models import RefundStatus


class UserPanelDataView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_favorite_count = UserFavoriteProducts.objects.filter(is_delete=False, user=user).count()

        # Fetch orders count based on status
        orders_count = Order.objects.filter(user=user).values('delivery_status').annotate(
            count=Count('delivery_status'))

        # Count the items that have been refunded and accepted
        refunded_count = OrderItem.objects.filter(
            order__user=user,
            refund__status=RefundStatus.ACCEPTED.name  # Assuming status is stored as the Enum name
        ).count()

        # Convert orders_count to a dictionary for easier access
        orders_count_dict = {item['delivery_status']: item['count'] for item in orders_count}

        data = {
            'favorite_count': user_favorite_count,
            'orders_count': {
                'current': orders_count_dict.get(
                    DeliveryStatus.PENDING.name, 0) + orders_count_dict.get(
                    DeliveryStatus.PROCESSING.name, 0) + orders_count_dict.get(
                    DeliveryStatus.SHIPPED.name, 0),
                'delivered': orders_count_dict.get(DeliveryStatus.DELIVERED.name, 0),
                'canceled': orders_count_dict.get(DeliveryStatus.CANCELED.name, 0),
                'refunded': refunded_count,
            }
        }
        return BaseResponse(data=data, status=status.HTTP_200_OK,
                            message=ResponseMessage.SUCCESS.value)
