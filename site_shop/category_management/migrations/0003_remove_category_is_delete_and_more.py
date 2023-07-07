# Generated by Django 4.2.3 on 2023-07-07 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('category_management', '0002_category_is_delete_categorybanner_is_delete'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='is_delete',
        ),
        migrations.RemoveField(
            model_name='categorybanner',
            name='is_delete',
        ),
        migrations.AddField(
            model_name='categorybanner',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
