from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_shop.order_management.models import Order, OrderItem, PaymentStatus
from site_shop.order_management.serializers import \
    CurrentOpenOrderSerializer, CurrentPendingOrderSerializer, UserPaidOrderSerializer
from site_shop.product_management.models import Product, ProductVariant


class ValidateUserCurrentLocalOrderView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        variant_ids = request.data.get('variants_id', [])

        valid_ids = ProductVariant.objects.filter(id__in=variant_ids, stock__gt=0, is_active=True).values_list('id',
                                                                                                               flat=True)

        return BaseResponse(data=list(valid_ids), status=status.HTTP_204_NO_CONTENT,
                            message=ResponseMessage.SUCCESS.value)


class GetUserCurrentOrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            with transaction.atomic():
                # acquire a lock on the order record
                open_order = Order.objects.select_for_update().filter(user=request.user,
                                                                      payment_status=PaymentStatus.OPEN_ORDER.name,
                                                                      is_delete=False).first()
                pending_orders = Order.objects.filter(
                    user=request.user,
                    payment_status=PaymentStatus.PENDING_PAYMENT.name,
                    is_delete=False,
                    repayment_date_expire__isnull=False,
                    repayment_date_expire__gte=timezone.now(),
                )
                if not open_order:
                    # create a new order if one doesn't exist
                    open_order = Order.objects.create(user=request.user, payment_status=PaymentStatus.OPEN_ORDER.name)
                # check if user order Address and Shipping Service Are Set Or Raise Error
                if open_order.shipping:
                    is_valid, message = open_order.is_valid_shipping_method(user_address=open_order.address,
                                                                            shipping=open_order.shipping)
                    if not is_valid:
                        open_order.shipping = None
                        open_order.address = None
                        open_order.save()
                open_order_serializer = CurrentOpenOrderSerializer(open_order)
                pending_orders_serializer = CurrentPendingOrderSerializer(pending_orders, many=True)
                data = {
                    'open': open_order_serializer.data,
                    'pending': pending_orders_serializer.data
                }

            return BaseResponse(data=data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except Order.DoesNotExist:

            return BaseResponse(status=status.HTTP_404_NOT_FOUND,
                                message=ResponseMessage.FAILED.value)
        except Exception as e:

            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class AddItemToCurrentOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            variant_id = request.data.get('variant_id')
            count = request.data.get('count')

            product = Product.objects.filter(pk=product_id, is_active=True).first()
            variant = ProductVariant.objects.filter(pk=variant_id, is_active=True).first()
            order, created = Order.objects.get_or_create(user=request.user,
                                                         payment_status=PaymentStatus.OPEN_ORDER.name, is_delete=False)

            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                variant=variant,
            )
            if variant.stock < order_item.count:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.ORDER_ITEM_DOES_NOT_EXIST_MORE_THAN.value.format(
                                        stock=variant.stock))

            order_item.count += count
            if order_item.count > variant.stock:
                order_item.count = variant.stock
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
            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user,
                                               order__payment_status=PaymentStatus.OPEN_ORDER.name,
                                               order__is_delete=False)
            variant = order_item.variant
            if variant.stock <= 0:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.ORDER_ITEM_DOES_NOT_EXIST_MORE_THAN.value.format(
                                        stock=variant.stock))

            order_item.count += 1
            order_item.save()
            return BaseResponse(status=status.HTTP_204_NO_CONTENT,
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

            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user,
                                               order__payment_status=PaymentStatus.OPEN_ORDER.name,
                                               order__is_delete=False)
            variant = order_item.variant
            if variant.stock == 1:
                return None
            order_item.count -= 1
            order_item.save()

            return BaseResponse(status=status.HTTP_204_NO_CONTENT,
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

            order_item = OrderItem.objects.get(id=item_id, order__user=self.request.user,
                                               order__payment_status=PaymentStatus.OPEN_ORDER.name,
                                               order__is_delete=False)
            order_item.delete()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.ORDER_ITEM_REMOVED.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


# Get User All Paid Orders For Profile Section
class UserPaidOrderListAPIView(ListAPIView):
    serializer_class = UserPaidOrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, is_delete=False,
                                    payment_status=PaymentStatus.PAID.name).order_by('-date_ordered')


# Get User Paid Order Detail For Profile Section

class UserPaidOrderDetailAPIView(RetrieveAPIView):
    serializer_class = UserPaidOrderSerializer
    lookup_field = 'slug'

    def get_object(self):
        order_slug = self.kwargs.get('slug')
        return Order.objects.exclude(
            payment_status=PaymentStatus.OPEN_ORDER.name).filter(slug=order_slug,
                                                                 user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if not order:
            return BaseResponse(status=status.HTTP_404_NOT_FOUND,
                                message=ResponseMessage.FAILED.value)
        serializer = self.get_serializer(order)

        response_data = serializer.data

        return BaseResponse(data=response_data, status=status.HTTP_200_OK,
                            message=ResponseMessage.SUCCESS.value)
