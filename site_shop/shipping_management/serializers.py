from rest_framework import serializers

from site_shop.shipping_management.models import ShippingRate, ShippingService


class ShippingServiceSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ShippingService
        fields = ('id', 'name', 'image')

    def get_image(self, obj):
        if obj.image:
            return obj.image.name
        return None


class ShippingRateSerializer(serializers.ModelSerializer):
    shipping_service = ShippingServiceSerializer()

    class Meta:
        model = ShippingRate
        fields = (
            'id', 'shipping_service', 'area', 'price', 'all_area', 'free_shipping_threshold', 'pay_at_destination'
        )
