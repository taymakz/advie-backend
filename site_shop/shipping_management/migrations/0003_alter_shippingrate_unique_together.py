# Generated by Django 4.2.2 on 2023-07-03 12:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('shipping_management', '0002_alter_shippingrate_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='shippingrate',
            unique_together={('shipping_service', 'all_area', 'area')},
        ),
    ]
