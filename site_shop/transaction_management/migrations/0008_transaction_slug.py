# Generated by Django 4.2.3 on 2023-07-06 18:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('transaction_management', '0007_transaction_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='slug',
            field=models.SlugField(blank=True, max_length=6, null=True, unique=True),
        ),
    ]
