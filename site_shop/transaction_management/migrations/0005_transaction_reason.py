# Generated by Django 4.2.3 on 2023-07-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('transaction_management', '0004_alter_transaction_transaction_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
