# Generated by Django 4.2.2 on 2023-07-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='status',
            field=models.CharField(blank=True, choices=[('SUCCESS', 'پرداخت موفق'), ('FAILED', 'پرداخت ناموفق')], max_length=20, null=True),
        ),
    ]
