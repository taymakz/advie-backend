from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id',
            'profile',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'national_code',
            'is_superuser',
            'is_active',
            'verified',
            'has_password',
        )

    def get_profile(self, obj):
        return obj.profile.name
