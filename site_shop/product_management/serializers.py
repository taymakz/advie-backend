from rest_framework import serializers

from . import models
from site_shop.category_management.models import Category


class VariantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VariantType
        fields = '__all__'


class VariantPrefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VariantPrefix
        fields = '__all__'


class VariantValueSerializer(serializers.ModelSerializer):
    prefix = VariantPrefixSerializer()

    class Meta:
        model = models.VariantValue
        fields = '__all__'



class ProductVariantSerializer(serializers.ModelSerializer):
    type = VariantTypeSerializer()
    value = VariantValueSerializer()

    class Meta:
        model = models.ProductVariant
        fields = (
            'id',
            'type',
            'value',
            'price',
            'special_price',
            'stock',
            'final_price',
            'special_price_percent',
            'is_special',
        )


class ProductsCategorySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = (
            'id', 'title_ir', 'title_en', 'display_title', 'url', 'is_active', 'parent')

    def get_url(self,obj):
        return obj.get_absolute_url()
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = (
            'id',
            'name',
        )


class ProductPropertySerializer(serializers.ModelSerializer):
    property = PropertySerializer()

    class Meta:
        model = models.ProductProperty
        fields = (
            'id',
            'product',
            'property',
            'value',
        )


# class ProductCommentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductComment
#         fields = (
#             'id',
#             'product',
#             'user',
#             'comment',
#             'suggest',
#             'score',
#             'create_date',
#             'accept_by_admin',
#         )


# class ProductDetailSerializer(serializers.ModelSerializer):
#     variant_type = VariantTypeSerializer()
#     category = ProductsCategorySerializer()
#     variants = ProductVariantSerializer(many=True, read_only=True)
#     properties = ProductPropertySerializer(many=True, read_only=True)
#     related_products = serializers.SerializerMethodField()
#     image = serializers.SerializerMethodField()
#     breadcrumbs = serializers.SerializerMethodField()
#     url = serializers.SerializerMethodField()
#
#     class Meta:
#         model = models.Product
#         fields = (
#             'id',
#             'url',
#             'title_ir',
#             'title_en',
#             'slug',
#             'description',
#             'sku',
#             'suggested',
#             'is_available_in_stock',
#             'variant_type',
#             'category',
#             'brand',
#             'color',
#             'medias',
#             'variants',
#             'image',
#             'properties',
#             'related_products',
#             'breadcrumbs',
#         )
#
#     def get_url(self, obj):
#         return obj.get_absolute_url()
#
#     def get_breadcrumbs_function(self, category):
#         breadcrumbs = []
#         while category:
#             breadcrumbs.append({'title': category.title_ir, 'url': category.get_absolute_url()})
#             category = category.parent
#         return reversed(breadcrumbs)
#
#     def get_breadcrumbs(self, obj):
#         return self.get_breadcrumbs_function(obj.category)
#
#     def get_image(self, obj):
#         return obj.image.name
#
#     def get_related_products(self, obj):
#         category = obj.category
#         related_products = models.Product.objects.filter(
#             category__in=category.get_descendants(include_self=True)
#         ).exclude(id=obj.id)[:20]
#         serializer = ProductListSerializer(related_products, many=True)
#         return serializer.data


class ProductCardSerializer(serializers.ModelSerializer):

    category = ProductsCategorySerializer(many=True)
    price = serializers.SerializerMethodField()
    special_price = serializers.SerializerMethodField()
    special_price_percent = serializers.SerializerMethodField()
    has_any_special_price = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()
    is_available_in_stock = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = (
            'id',
            'image',
            'title_ir',
            'title_en',
            'url',
            'price',
            'special_price',
            'special_price_percent',
            'has_any_special_price',
            'final_price',
            'sku',
            'is_available_in_stock',
            'category',
        )

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image(self, obj):
        return obj.image.name

    def get_price(self, obj):
        return obj.minimum_variant_price

    def get_special_price(self, obj):
        return obj.minimum_variant_special_price

    def get_special_price_percent(self, obj):
        return obj.minimum_variant_special_price_percent

    def get_has_any_special_price(self, obj):
        return obj.minimum_variant_is_special

    def get_final_price(self, obj):
        return obj.minimum_variant_final_price

    def get_is_available_in_stock(self, obj):
        return obj.is_available_in_stock


class SearchProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.Product
        fields = [
            'id',
            'title_ir',
            'url',
            'image'
        ]

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image(self, obj):
        return obj.image.name



