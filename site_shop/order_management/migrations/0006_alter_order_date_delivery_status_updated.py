# Generated by Django 4.2.3 on 2023-07-14 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_management', '0005_order_date_delivery_status_updated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_delivery_status_updated',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]