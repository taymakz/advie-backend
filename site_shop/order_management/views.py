from django.db import transaction
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_shop.order_management.models import Order, OrderItem, PaymentStatus
from site_shop.order_management.serializers import UserPaidOrderListSerializer, OrderDetailSerializer, \
    CurrentOrderSerializer
from site_shop.product_management.models import Product, ProductVariant
from site_shop.transaction_management.models import Transaction


class GetUserCurrentOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            with transaction.atomic():
                # acquire a lock on the order record
                order = Order.objects.select_for_update().filter(user=request.user,
                                                                 payment_status=PaymentStatus.OPEN_ORDER.value,is_delete=False).first()

                if not order:
                    # create a new order if one doesn't exist
                    order = Order.objects.create(user=request.user,payment_status=PaymentStatus.OPEN_ORDER.value)
                serializer = CurrentOrderSerializer(order)

            return BaseResponse(data=serializer.data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:

            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class AddItemToCurrentOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            variant_id = request.data.get('variant_id')

            product = Product.objects.filter(pk=product_id, is_active=True).first()
            variant = ProductVariant.objects.filter(pk=variant_id, is_active=True).first()
            order, created = Order.objects.get_or_create(user=request.user, payment_status=PaymentStatus.NOT_PAID.value)

            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                variant=variant,
            )
            if variant.stock <= order_item.count:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.ORDER_ITEM_DOES_NOT_EXIST_MORE_THAN.value.format(
                                        stock=variant.stock))

            order_item.count += 1
            order_item.save()

            return BaseResponse(data=order_item.id, status=status.HTTP_200_OK,
                                message=ResponseMessage.ORDER_ADDED_TO_CART_SUCCESSFULLY.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class IncreaseCurrentOrderItemCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            item_id = request.data.get('item_id')
            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user)
            variant = order_item.variant
            if variant.stock <= 0:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.ORDER_ITEM_DOES_NOT_EXIST_MORE_THAN.value.format(
                                        stock=variant.stock))

            order_item.count += 1
            order_item.save()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.ORDER_ITEM_COUNT_INCREASED.value)
        except:

            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class DecreaseCurrentOrderItemCountView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            item_id = request.data.get('item_id')

            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user)
            variant = order_item.variant
            if variant.stock == 1:
                return None
            order_item.count -= 1
            order_item.save()

            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.ORDER_ITEM_COUNT_DECREASED.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class RemoveCurrentOrderItemView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        try:
            item_id = request.data.get('item_id')

            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user)
            order_item.delete()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.ORDER_ITEM_REMOVED.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


# Get User All Paid Orders For Profile Section
class UserPaidOrderListAPIView(ListAPIView):
    serializer_class = UserPaidOrderListSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.get_paid(user_id=self.request.user.id)


# Get User Paid Order Detail For Profile Section

class UserPaidOrderDetailAPIView(RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    lookup_field = 'transaction'

    def get_object(self):
        transaction_id = self.kwargs.get('id')
        transaction = Transaction.objects.get_success().filter(transaction_id=transaction_id,
                                                               user=self.request.user).first()
        return transaction.order

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if not order:
            return BaseResponse(status=status.HTTP_404_NOT_FOUND,
                                message=ResponseMessage.FAILED.value)
        serializer = self.get_serializer(order)

        response_data = serializer.data

        return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                            message=ResponseMessage.SUCCESS.value)
