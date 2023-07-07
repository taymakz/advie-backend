from django.db import models

from site_account.user_management.models import User
from site_utils.persian import province, cities


class UserAddresses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    receiver_name = models.CharField(max_length=55)
    receiver_family = models.CharField(max_length=55)
    receiver_phone = models.CharField(max_length=11)
    receiver_national_code = models.CharField(max_length=12)
    receiver_province = models.CharField(max_length=100, choices=province.province)
    receiver_city = models.CharField(max_length=100, choices=cities.cities)
    receiver_postal_code = models.CharField(max_length=20)
    receiver_address = models.TextField(max_length=100)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} | {self.receiver_province} | {self.receiver_city}"
