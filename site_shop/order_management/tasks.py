from celery import shared_task

from site_utils.messaging_services.phone_service import send_order_status_phone


@shared_task(name="send order status SMS")
def send_order_status_celery(to, pattern, slug, track_code):
    send_order_status_phone(to=to, pattern=pattern, number=slug, track_code=track_code)
