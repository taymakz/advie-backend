# Generated by Django 4.2.3 on 2023-07-06 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_management', '0006_transaction_ref_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
