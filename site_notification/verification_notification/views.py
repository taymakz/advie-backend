from django.shortcuts import redirect
from django.views import View

from config.settings import FRONTEND_URL
from site_api.api_configuration.enums import ResponseMessage
from site_notification.announcement_notification.models import Newsletter
from site_notification.verification_notification.models import VerifyNewsletterService


class ActivateNewsletterEmail(View):
    def get(self, request, activate_link):
        if not activate_link: return redirect(
            f"{FRONTEND_URL}/vf/tm?f={ResponseMessage.EMAIL_NEWSLETTER_ACTIVATION_FAILED.value}")
        link: VerifyNewsletterService = VerifyNewsletterService.objects.filter(activate_link=activate_link).first()
        if not link or link.is_expired():
            return redirect(
                f"{FRONTEND_URL}/vf/tm?f={ResponseMessage.EMAIL_NEWSLETTER_ACTIVATION_FAILED.value}")
        Newsletter.objects.create(email=link.email)
        link.delete()

        return redirect(
            f"{FRONTEND_URL}/vf/tm?s={ResponseMessage.EMAIL_NEWSLETTER_ACTIVATION_SUCCESS.value}")
