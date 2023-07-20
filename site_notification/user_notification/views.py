# Create your views here.
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_notification.user_notification.models import UserNotification
from site_notification.user_notification.serializers import UserNotificationSerializer


class NotificationAPIListView(ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = UserNotification.objects.filter(is_delete=False).order_by('-date_created')
    serializer_class = UserNotificationSerializer

    def list(self, request, *args, **kwargs):
        try:
            notifications = self.get_queryset()
            serializer = self.get_serializer(notifications, many=True)
            # mark_read_user_all_notifications_celery.delay(self.request.user.id)
            for notif in UserNotification.objects.filter(user=self.request.user, is_read=False, is_delete=False).all():
                notif.is_read = True
                notif.save()
            return BaseResponse(data=serializer.data, status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)


class RemoveAllNotificationAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            user = self.request.user
            for notif in UserNotification.objects.filter(user=user, is_delete=False).all():
                notif.is_delete = True
                notif.save()
            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.SUCCESS.value)
        except:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.FAILED.value)
