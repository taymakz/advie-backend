# Generated by Django 4.2.3 on 2023-07-04 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('refund_management', '0004_alter_refundorderitem_order_item'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='refundorderitem',
            name='order_item',
        ),
    ]
