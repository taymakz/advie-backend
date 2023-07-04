# Generated by Django 4.2.2 on 2023-07-04 08:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order_management', '0006_order_is_delete_orderitem_is_delete'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='status',
            new_name='delivery_status',
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_status',
            field=models.CharField(blank=True, choices=[('OPEN_ORDER', 'باز'), ('PENDING_PAYMENT', 'در انتظار پرداخت'), ('PAID', 'پرداخت شده')], max_length=20, null=True),
        ),
    ]
