import time

from celery import shared_task


@shared_task(name="send otp")
def send_otp_celery(to, code, type):
    time.sleep(5)
    print(code)
