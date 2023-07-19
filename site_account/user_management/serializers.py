from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    has_password = serializers.SerializerMethodField()
    notification_count = serializers.SerializerMethodField()
    full_name = serializers.CharField(source='get_full_name')

    class Meta:
        model = User
        fields = (
            'id',
            'profile',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'phone',
            'national_code',
            'is_superuser',
            'is_active',
            'verified',
            'has_password',
            'notification_count',
        )

    def get_profile(self, obj):
        return obj.profile.name

    def get_has_password(self, obj: User):
        return obj.has_usable_password()

    def get_notification_count(self, obj: User):
        return obj.notifications.filter(is_delete=False, is_read=False).count()


class UserEditProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'national_code',
        )
