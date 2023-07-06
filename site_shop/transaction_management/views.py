import datetime
import json

import requests
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
                coupon_effect_new_price, coupon_effect_dif_price, percentage_effect = used_coupon.calculate_discount(
                    order_total_price)
                order_total_price -= coupon_effect_dif_price
            else:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=ResponseMessage.PAYMENT_NOT_VALID_USED_COUPON.value)
        order_total_price += current_order.shipping.calculate_price(
            order_price=order_total_price_before_coupon)
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
            "MerchantID": settings.ZARINPAL_MERCHANT,
            "Amount": order_total_price * 10,
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
                    current_order.coupon_effect_price = coupon_effect_dif_price
                    current_order.shipping_effect_price = current_order.shipping.calculate_price(
                        order_price=order_total_price_before_coupon)
                    current_order.payment_status = PaymentStatus.PENDING_PAYMENT.name
                    current_order.save()
                    return BaseResponse(
                        data={'is_free': False,
                              'payment_gateway_link': ZP_API_STARTPAY + str(response['Authority'])},
                        status=status.HTTP_200_OK,
                        message='در حال پردازش')
                else:
                    return BaseResponse(data={'status': False, 'code': str(response['Status'])})
            return response

        except requests.exceptions.Timeout:
            return BaseResponse(data={'status': False, 'code': 'خطای اتصال'})
        except requests.exceptions.ConnectionError:
            return BaseResponse(data={'status': False, 'code': 'خطای اتصال'})


class VerifyPaymentAPIView(APIView):

    def get(self, request):
        order_slug = request.GET.get('order')

        try:
            current_order = Order.objects.get(slug=order_slug, payment_status=PaymentStatus.PENDING_PAYMENT.name)

        except Order.DoesNotExist:
            return BaseResponse(data={"redirect_to": f"{settings.FRONTEND_URL}/checkout/cart/"},
                                status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
        total_price = current_order.get_total_price
        user = current_order.user
        total_price -= current_order.coupon_effect_price
        total_price += current_order.shipping_effect_price
        authority = request.GET.get('Authority', None)

        data = {
            "MerchantID": settings.ZARINPAL_MERCHANT,
            "Amount": total_price * 10,
            "Authority": authority,
        }
        data = json.dumps(data)
        # set content length by data
        headers = {'content-type': 'application/json', 'content-length': str(len(data))}
        response = requests.post(ZP_API_VERIFY, data=data, headers=headers)

        if response.status_code == 200:
            response = response.json()

            if response['Status'] == 100:
                current_order.ordered_date = datetime.date.today()
                current_order.payment_status = PaymentStatus.PAID.name
                current_order.delivery_status = DeliveryStatus.PENDING.name
                if current_order.coupon is not None:
                    valid, message = current_order.coupon.validate_coupon(user_id=user.id,
                                                                          order_total_price=total_price)
                    if valid:
                        new_price, dif_price, percentage_price = current_order.coupon.calculate_discount(
                            current_order.get_total_price)
                        current_order.coupon_effect_price = dif_price
                    else:
                        pass
                for item in current_order.items.all():
                    item.variant.stock -= item.count
                    item.variant.save()
                    item.set_final_price()
                    item.save()
                current_order.save()
                transaction = Transaction.objects.create(user=user, order=current_order,
                                                         status=TransactionStatus.SUCCESS.name,
                                                         ref_id=response['RefID'])
                return redirect(
                    f"{settings.FRONTEND_URL}/checkout/result/{transaction.transaction_id}/{transaction.slug}/")

            else:
                errors = {
                    1: 'اطلاعات ارسال شده ناقص است.',
                    -2: 'IP و يا مرچنت كد پذيرنده صحيح نيست.',
                    -3: 'با توجه به محدوديت هاي شاپرك امكان پرداخت با رقم درخواست شده ميسر نمي باشد.',
                    -4: 'سطح تاييد پذيرنده پايين تر از سطح نقره اي است.',
                    -11: 'درخواست مورد نظر يافت نشد.',
                    -12: 'امكان ويرايش درخواست ميسر نمي باشد.',
                    -21: 'هيچ نوع عمليات مالي براي اين تراكنش يافت نشد.',
                    -22: 'تراكنش نا موفق ميباشد.',
                    -33: 'رقم تراكنش با رقم پرداخت شده مطابقت ندارد.',
                    -34: 'سقف تقسيم تراكنش از لحاظ تعداد يا رقم عبور نموده است.',
                    -40: 'اجازه دسترسي به متد مربوطه وجود ندارد.',
                    -41: 'اطلاعات ارسال شده مربوط به AdditionalData غيرمعتبر ميباشد.',
                    -42: 'مدت زمان معتبر طول عمر شناسه پرداخت بايد بين 30 دقيه تا 45 روز مي باشد.',
                    -54: 'درخواست مورد نظر آرشيو شده است.',
                    100: 'عمليات با موفقيت انجام گرديده است.',
                    101: 'عمليات پرداخت موفق بوده و قبلا PaymentVerification تراكنش انجام شده است.'
                }

                error_code = response['Status']
                error_message = errors.get(error_code, 'خطای ناشناخته لطفا با پشتیبانی تماس بگیرید')
                reason = f"Status: False,کد: {str(error_code)}, پیام: {error_message}"
                transaction = Transaction.objects.create(user=user, order=current_order,
                                                         status=TransactionStatus.FAILED.name,
                                                         reason=reason)
                return redirect(
                    f"{settings.FRONTEND_URL}/checkout/result/{transaction.transaction_id}/{transaction.slug}/")

        Transaction.objects.create(user=user, order=current_order, status=TransactionStatus.FAILED.name,
                                   reason=response)
        return redirect(f"{settings.FRONTEND_URL}/vf/pm?f=خطای ناشناخته لطفا با پشتیبانی تماس بگیرید")
