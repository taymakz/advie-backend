# Generated by Django 4.2.3 on 2023-07-18 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_management', '0006_alter_order_date_delivery_status_updated'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_canceled_reason',
            field=models.CharField(blank=True, max_length=155, null=True),
        ),
    ]