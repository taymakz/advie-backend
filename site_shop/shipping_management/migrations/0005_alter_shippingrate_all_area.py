# Generated by Django 4.2.2 on 2023-07-03 12:19

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shipping_management', '0004_alter_shippingrate_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingrate',
            name='all_area',
            field=models.BooleanField(default=False),
        ),
    ]
