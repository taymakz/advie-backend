from django.db import models

from site_account.user_management.models import User
from site_utils.persian import province, cities


class UserAddresses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    receiver_name = models.CharField(max_length=100)
    receiver_family = models.CharField(max_length=100)
    receiver_phone = models.CharField(max_length=100)
    receiver_national_code = models.CharField(max_length=12)
    province = models.CharField(max_length=100, choices=province.province)
    city = models.CharField(max_length=100, choices=cities.cities)
    postal_code = models.CharField(max_length=20)
    address = models.TextField(max_length=100)

    def __str__(self):
        return f"{self.user.username} | {self.province} | {self.city}"