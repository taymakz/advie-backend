# views.py
from rest_framework import status
from rest_framework.generics import CreateAPIView

from site_api.api_configuration.enums import ResponseMessage
from site_api.api_configuration.response import BaseResponse
from site_notification.announcement_notification.models import Newsletter
from site_notification.announcement_notification.serializers import NewsletterSerializer
from site_notification.verification_notification.models import VerifyNewsletterService


class NewsletterCreateView(CreateAPIView):
    serializer_class = NewsletterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']

            newsletter = Newsletter.objects.filter(email=email).first()
            if newsletter:
                return BaseResponse(status=status.HTTP_200_OK,
                                    message=ResponseMessage.EMAIL_NEWSLETTER_EXIST.value)

            verify: VerifyNewsletterService = VerifyNewsletterService.objects.filter(email=email).first()
            if verify:
                if verify.is_expired():
                    pass
                else:
                    return BaseResponse(status=status.HTTP_200_OK,
                                        message=ResponseMessage.EMAIL_NEWSLETTER_ACTIVATION_LINK_ALREADY_SENT.value)

            verify = VerifyNewsletterService.objects.create(email=email)
            verify.send_activate_link(request)

            return BaseResponse(status=status.HTTP_200_OK,
                                message=ResponseMessage.EMAIL_NEWSLETTER_ACTIVATION_LINK_SENT.value)
        else:
            return BaseResponse(status=status.HTTP_400_BAD_REQUEST,
                                message=ResponseMessage.NOT_VALID_EMAIL.value)
