from rest_framework import serializers

from site_notification.user_notification.models import UserNotification


class UserNotificationSerializer(serializers.ModelSerializer):
    order_items = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()

    class Meta:
        model = UserNotification
        fields = (
            'id',
            'order_items',
            'product',
            'template',
            'title',
            'message',
            'link',
            'date_created',

        )

    def get_order_items(self, obj: UserNotification):
        try:
            if obj.order:
                return [
                    {
                        'image': item.product.image.name,
                        'title_ir': item.product.title_ir,
                        'url': item.product.get_absolute_url(),

                    }
                    for item in obj.order.items.all()
                ]
        except:
            pass
        return None

    def get_product(self, obj: UserNotification):
        try:
            if obj.product:
                return {
                    'image': obj.product.image.name,
                    'title_ir': obj.product.title_ir,
                    'url': obj.product.get_absolute_url(),
                }
        except:
            pass
        return None
