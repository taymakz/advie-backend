# Generated by Django 4.2.2 on 2023-06-19 15:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('website_banner', '0002_alter_sitebanner_options_alter_sitebanner_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitebanner',
            name='resize_height',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='sitebanner',
            name='resize_width',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
