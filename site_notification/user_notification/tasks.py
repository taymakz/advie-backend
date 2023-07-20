from celery import shared_task

from site_notification.user_notification import models


@shared_task(name="Mark as Seen user All notifications on list request")
def mark_read_user_all_notifications_celery(user_id):
    for notif in models.UserNotification.objects.filter(user_id=user_id, is_read=False, is_delete=False).all():
        notif.is_read = True
        notif.save()


@shared_task(name="Add Notification to User")
def add_notification_to_user_celery(user_id, template, title, message, link, order_id=None, product_id=None):
    models.UserNotification.objects.create(user_id=user_id, order_id=order_id, product_id=product_id, template=template,
                                           title=title, message=message, link=link)
