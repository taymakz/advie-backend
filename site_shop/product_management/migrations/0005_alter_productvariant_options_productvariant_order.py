# Generated by Django 4.2.1 on 2023-06-09 10:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('product_management', '0004_alter_productvariant_special_price_end_date_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productvariant',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='productvariant',
            name='order',
            field=models.IntegerField(blank=True, default=1, null=True),
        ),
    ]
