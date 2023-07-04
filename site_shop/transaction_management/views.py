import datetime
import json

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_account.user_addresses.models import UserAddresses
from site_shop.coupon_management.models import Coupon
from site_shop.order_management.models import Order, PaymentStatus, OrderAddress, DeliveryStatus
from site_shop.shipping_management.models import ShippingRate
from site_shop.transaction_management.models import Transaction, TransactionStatus

if settings.ZARINPAL_SANDBOX:
    sandbox = 'sandbox'
else:
    sandbox = 'www'

ZP_API_REQUEST = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentRequest.json"
ZP_API_VERIFY = f"https://{sandbox}.zarinpal.com/pg/rest/WebGate/PaymentVerification.json"
ZP_API_STARTPAY = f"https://{sandbox}.zarinpal.com/pg/StartPay/"

amount = 1000  # Rial / Required
description = "نهایی کردن خرید سفارش "
email = ''
mobile = ''
CallbackURL = settings.BACKEND_URL


class RequestPaymentCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        user = request.user

        # check if user Have Any Open Order or Rise Error
        try:
            current_order = Order.objects.get(user=user, payment_status=PaymentStatus.OPEN_ORDER.name,
                                              is_delete=False)
        except Order.DoesNotExist:
            return BaseResponse(data={"redirect_to": "/checkout/cart/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
        if current_order.items.count() == 0:
            return BaseResponse(data={"redirect_to": "/checkout/cart/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PAYMENT_EMPTY_ORDER.value)

        shipping_id = request.data.get('shipping_id')
        address_id = request.data.get('address_id')

        # check if user Selected Address and Shipping Service Or Raise Error
        if shipping_id is None or address_id is None:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST, message=ResponseMessage.FAILED.value)

        # check if user Selected Shipping is Exist or Raise Error
        try:
            selected_shipping = ShippingRate.objects.get(id=shipping_id, is_delete=False)
        except ShippingRate.DoesNotExist:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PAYMENT_NOT_VALID_SELECTED_SHIPPING.value)

        # check if user Selected Address is Exist  or Raise Error
        try:
            selected_address = UserAddresses.objects.get(user=user, id=address_id, is_delete=False)
        except UserAddresses.DoesNotExist:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PAYMENT_NOT_VALID_SELECTED_ADDRESS.value)
        is_valid, message = current_order.is_valid_shipping_method(user_address=selected_address,
                                                                   shipping=selected_shipping)
        # Validate Address and Shipping Service

        if not is_valid:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PAYMENT_NOT_VALID_SELECTED_SHIPPING.value)
        if current_order.address:
            current_order.address.is_delete = True
            current_order.address.save()
        order_address = OrderAddress.objects.create(
            receiver_name=selected_address.receiver_name,
            receiver_phone=selected_address.receiver_phone,
            receiver_city=selected_address.receiver_city,
            receiver_province=selected_address.receiver_province,
            receiver_postal_code=selected_address.receiver_postal_code,
            receiver_address=selected_address.receiver_address,
        )
        # Success
        current_order.address = order_address
        current_order.shipping = selected_shipping
        current_order.save()

        return BaseResponse(status=status.HTTP_204_NO_CONTENT,
                            message=ResponseMessage.SUCCESS.value)


class RequestPaymentSubmitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        # check if user Have Any Open Order or Rise Error
        user = request.user

        try:
            current_order = Order.objects.get(user=user, payment_status=PaymentStatus.OPEN_ORDER.name,
                                              is_delete=False)
        except Order.DoesNotExist:
            return BaseResponse(data={"redirect_to": "/checkout/cart/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
        if current_order.items.count() == 0:
            return BaseResponse(data={"redirect_to": "/checkout/cart/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        coupon_code = request.data.get('coupon_code')
        order_total_price = current_order.get_total_price

        # check if user order Address and Shipping Service Are Set Or Raise Error
        if current_order.shipping is None or current_order.address is None:
            return BaseResponse(data={"redirect_to": "/checkout/shipping/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)

        # Validate Address and Shipping Service
        is_valid, message = current_order.is_valid_shipping_method(user_address=current_order.address,
                                                                   shipping=current_order.shipping)
        if not is_valid:
            return BaseResponse(data={"redirect_to": "/checkout/cart/"}, status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.PAYMENT_NOT_VALID_SELECTED_SHIPPING.value)

        order_total_price_before_coupon = order_total_price

        # check if user Used Coupon is Exist And Valid Or Raise Error
        coupon_effect_dif_price = 0
        if coupon_code:
            try:
                used_coupon = Coupon.objects.get(code=coupon_code, is_delete=False)
            except Coupon.DoesNotExist:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.PAYMENT_NOT_VALID_USED_COUPON.value)
            valid, message = used_coupon.validate_coupon(user_id=user.id, order_total_price=order_total_price)
            if valid:
                coupon_effect_new_price, coupon_effect_dif_price = used_coupon.calculate_discount(order_total_price)
                order_total_price -= coupon_effect_dif_price
            else:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.PAYMENT_NOT_VALID_USED_COUPON.value)

        # if Order Price is Free
        if order_total_price == 0:
            current_order.payment_status = PaymentStatus.PAID.name
            current_order.delivery_status = DeliveryStatus.PENDING.name
            current_order.coupon_effect_price = coupon_effect_dif_price
            current_order.shipping_effect_price = current_order.shipping.calculate_price(
                order_price=order_total_price_before_coupon)
            current_order.date_ordered = datetime.date.today()

            current_order.save()

            for item in current_order.items.all():
                item.variant.stock -= item.count
                item.variant.save()
                item.set_final_price()
                item.save()

            Transaction.objects.create(
                user=user,
                order=current_order,
                status=TransactionStatus.SUCCESS.name
            )
            return BaseResponse(
                data={'is_free': True,
                      'payment_gateway_link': f"{settings.FRONTEND_URL}/panel/orders/{current_order.slug}/"},
                status=status.HTTP_200_OK,
                message='در حال پردازش')

        if order_total_price < 1000:
            order_total_price = 1000

        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount * 10,
            "Description": description,
            "Phone": user.phone,
            "CallbackURL": f"{CallbackURL}/api/payment/verify?order={current_order.slug}",
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        try:
            response = requests.post(ZP_API_REQUEST, data=data, headers=headers, timeout=10)

            if response.status_code == 200:
                response = response.json()
                if response['Status'] == 100:
                    return {'status': True, 'url': ZP_API_STARTPAY + str(response['Authority']),
                            'authority': response['Authority']}
                else:
                    return {'status': False, 'code': str(response['Status'])}
            return response

        except requests.exceptions.Timeout:
            return {'status': False, 'code': 'timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': False, 'code': 'connection error'}
class VerifyPaymentAPIView(APIView):

    def get(self, request, authority):
        data = {
            "MerchantID": settings.MERCHANT,
            "Amount": amount,
            "Authority": authority,
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()
            if response['Status'] == 100:
                return {'status': True, 'RefID': response['RefID']}
            else:
                return {'status': False, 'code': str(response['Status'])}
        return response
