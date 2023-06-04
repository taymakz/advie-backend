from rest_framework import serializers
from . import models


class SiteBannerSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    class Meta:
        model = models.SiteBanner
        fields = (
            'title',
            'image',
            'image_alt',
            'url',
            'position',
        )
    def get_image(self,obj):
        return obj.image.name