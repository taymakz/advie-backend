# Generated by Django 4.2.2 on 2023-07-04 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('announcement_notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
