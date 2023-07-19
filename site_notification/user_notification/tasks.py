from celery import shared_task

from site_notification.user_notification.models import UserNotification


@shared_task(name="Mark as Seen user All notifications on list request")
def mark_read_user_all_notifications(user_id):
    for notif in UserNotification.objects.filter(user_id=user_id, is_read=False, is_delete=False).all():
        notif.is_read = True
        notif.save()
