# Generated by Django 4.2.1 on 2023-06-06 20:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_management', '0003_productvariant_special_price_end_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariant',
            name='special_price_end_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='special_price_start_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
