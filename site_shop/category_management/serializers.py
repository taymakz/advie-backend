from rest_framework import serializers

from site_shop.category_management.models import CategoryBanner, Category
from site_shop.product_management.models import Product


class CategoryProductSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title_ir', 'url']

    def get_url(self, obj):
        return obj.get_absolute_url()


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'image', 'title_ir', 'display_title', 'url', 'children']

    def get_queryset(self):
        return super().get_queryset().filter(parent=None)

    def get_children(self, obj):
        children = obj.get_children()
        serializer = CategoryWithProductsSerializer(children, many=True)
        return serializer.data

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image(self, obj):
        return obj.image.name


class CategoryWithProductsSerializer(serializers.ModelSerializer):
    products = CategoryProductSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'image', 'title_ir', 'display_title', 'url', 'products']

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image(self, obj):
        return obj.image.name


class CategoryBannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBanner
        exclude = 'is_active'


class SearchCategorySerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id',
            'image',
            'title_ir',
            'url',
        ]

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_image(self, obj):
        return obj.image.name
