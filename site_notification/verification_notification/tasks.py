from celery import shared_task

from site_utils.messaging_services.email_service import send_otp_email
from site_utils.messaging_services.phone_service import send_otp_phone


@shared_task(name="send otp")
def send_otp_celery(to, code, type):
    if type == 'PHONE':
        send_otp_phone(to=to, code=code)
    elif type == 'EMAIL':
        send_otp_email(to=to, context={code})
