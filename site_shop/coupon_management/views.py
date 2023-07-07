from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from .models import Coupon
from ..order_management.models import Order, PaymentStatus


class UseCouponCodeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get('code')
        user = request.user
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            return BaseResponse(
                status=status.HTTP_404_NOT_FOUND,
                message=ResponseMessage.COUPON_NOT_VALID.value
            )
        try:
            user_current_order = Order.objects.get(user=user, payment_status=PaymentStatus.OPEN_ORDER.name,
                                                   is_delete=False)
            total_order = user_current_order.get_total_price
            valid, message = coupon.validate_coupon(user_id=user.id,
                                                    order_total_price=total_order)
            if valid:
                new_price, dif_price, percentage_effect = coupon.calculate_discount(total_order)

                return BaseResponse(
                    data={"discount_amount": dif_price, "percentage_effect": percentage_effect},
                    status=status.HTTP_204_NO_CONTENT,
                    message=message
                )
            else:
                return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                    message=message)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
