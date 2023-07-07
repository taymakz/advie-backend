# Generated by Django 4.2.2 on 2023-07-04 07:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('product_management', '0005_alter_productvariant_options_productvariant_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productproperty',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productvariant',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='productvisit',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userfavoriteproducts',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userrecentvisitedproduct',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variantprefix',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='varianttype',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='variantvalue',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
    ]
