# Generated by Django 4.2.3 on 2023-07-05 21:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_management', '0005_transaction_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='ref_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]