from rest_framework import serializers

from site_account.user_addresses.models import UserAddresses


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddresses
        fields = (
            'id',
            'receiver_name',
            'receiver_family',
            'receiver_phone',
            'receiver_national_code',
            'receiver_province',
            'receiver_city',
            'receiver_postal_code',
            'receiver_address',
        )
