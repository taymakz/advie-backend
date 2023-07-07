# Generated by Django 4.2.1 on 2023-06-03 15:46

import ckeditor_uploader.fields
import django.db.models.deletion
import imagekit.models.fields
from django.conf import settings
from django.db import migrations, models

import site_shop.product_management.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('category_management', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', imagekit.models.fields.ProcessedImageField(default='images/products/default_product.png',
                                                                     upload_to=site_shop.product_management.models.upload_product_path)),
                ('title_ir', models.CharField(max_length=255)),
                ('title_en', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, max_length=300, null=True, unique=True)),
                ('sku', models.IntegerField(blank=True, db_index=True, editable=False, null=True, unique=True)),
                ('description', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('category',
                 models.ManyToManyField(db_index=True, related_name='products', to='category_management.category')),
            ],
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VariantPrefix',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VariantType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ir', models.CharField(max_length=100)),
                ('title_en', models.CharField(max_length=100)),
                ('select_style',
                 models.CharField(choices=[('RADIO', 'RADIO'), ('DROP_DOWN', 'DROP_DOWN')], default='RADIO',
                                  max_length=20)),
                ('is_none', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='VariantValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('color_code',
                 models.CharField(blank=True, max_length=100, null=True, verbose_name='Color (Not Required)')),
                ('prefix',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_management.variantprefix')),
                ('type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_management.varianttype')),
            ],
        ),
        migrations.CreateModel(
            name='UserRecentVisitedProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_management.product')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recent_products',
                                           to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserFavoriteProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_management.product')),
                ('user',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_products',
                                   to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=30, verbose_name='user ip')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visits',
                                              to='product_management.product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                           to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'product visit',
                'verbose_name_plural': 'product visits',
            },
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.PositiveIntegerField(default=0)),
                ('special_price', models.PositiveIntegerField(blank=True, null=True)),
                ('stock', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants',
                                              to='product_management.product')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                           related_name='variants', to='product_management.varianttype')),
                ('value', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE,
                                            to='product_management.variantvalue')),
            ],
        ),
        migrations.CreateModel(
            name='ProductProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=100)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='properties',
                                              to='product_management.product')),
                ('property',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product_management.property')),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='variant_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='products',
                                    to='product_management.varianttype'),
        ),
    ]
