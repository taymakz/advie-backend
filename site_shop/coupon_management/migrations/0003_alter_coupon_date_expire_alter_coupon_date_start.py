# Generated by Django 4.2.3 on 2023-07-05 17:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('coupon_management', '0002_coupon_is_active_coupon_is_delete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='date_expire',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='date_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
