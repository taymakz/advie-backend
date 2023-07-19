# Create your views here.
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from api_configuration.enums import ResponseMessage
from api_configuration.response import BaseResponse
from site_notification.user_notification.models import UserNotification
from site_notification.user_notification.serializers import UserNotificationSerializer
from site_notification.user_notification.tasks import mark_read_user_all_notifications


class NotificationAPIListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserNotification.objects.filter(is_delete=False).order_by('-date_created')
    serializer_class = UserNotificationSerializer

    def list(self, request, *args, **kwargs):
        try:
            notifications = self.get_queryset()
            serializer = self.get_serializer(notifications, many=True)
            mark_read_user_all_notifications.delay(self.request.user.id)
            return BaseResponse(data=serializer.data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
