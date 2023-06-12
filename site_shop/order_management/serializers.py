from rest_framework import serializers

from site_shop.order_management.models import OrderAddress, OrderItem, Order
from site_shop.product_management.serializers import VariantTypeSerializer, ProductVariantSerializer
from site_shop.transaction_management.models import Transaction


class OrderAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderAddress
        fields = '__all__'


# Current Order , Item Serializer ( Not Paid )
class CurrentOrderItemSerializer(serializers.ModelSerializer):
    variant_type = VariantTypeSerializer(read_only=True)
    variant = ProductVariantSerializer(read_only=True)

    order_id = serializers.SerializerMethodField()
    product_id = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()
    product_title_ir = serializers.SerializerMethodField()
    product_title_en = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'order_id',
            'product_id',
            'product_url',
            'product_title_ir',
            'product_title_en',
            'product_image',
            'variant_type',
            'variant',
            'count',
            'total_price',
        )

    def get_order_id(self, obj):
        return obj.order.id

    def get_product_id(self, obj):
        return obj.product.id

    def get_product_url(self, obj):
        return obj.product.get_absolute_url()

    def get_product_title_ir(self, obj):
        return obj.product.title_ir

    def get_product_title_en(self, obj):
        return obj.product.title_en


    def get_product_image(self, obj):
        return obj.product.image.name

    def get_total_price(self, obj):
        return obj.get_total_price


class CurrentOrderSerializer(serializers.ModelSerializer):
    items = CurrentOrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'items',
            'total_price',
        )

    def get_total_price(self, obj):
        return obj.get_total_price


# Order , Item Serializer ( Paid )
class UserPaidOrderListSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    total_price_before_discount = serializers.SerializerMethodField()
    shipping_price = serializers.SerializerMethodField()

    transaction_id = serializers.SerializerMethodField()

    shipping_service = serializers.SerializerMethodField()
    address = OrderAddressSerializer()

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'transaction',
            'transaction_id',
            'tracking_code',

            'date_ordered',
            'date_shipped',
            'date_delivered',

            'total_price',
            'total_profit',
            'total_price_before_discount',
            'shipping_price',

            'shipping_service',
            'address',
        )

    def get_total_price(self, obj):
        return obj.get_total_price

    def get_total_profit(self, obj):
        return obj.get_total_profit

    def get_total_price_before_discount(self, obj):
        return obj.get_total_price_before_discount

    def get_shipping_price(self, obj):
        if obj.shipping_effect_price:
            return obj.shipping_effect_price
        else:
            return 0

    def get_shipping_service(self, obj):
        return {
            "image": obj.shipping.shipping_service.image.name,
            "name": obj.shipping.shipping_service.name
        }

    def get_transaction_id(self, obj):
        transaction = Transaction.objects.get_success().filter(order_id=obj.id).first()

        return transaction.transaction_id


class UserPaidOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()
    product_title_ir = serializers.SerializerMethodField()
    product_title_en = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    variant = ProductVariantSerializer()

    refund_status = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product_id',
            'product_url',
            'product_title_ir',
            'product_title_en',
            'product_image',
            'variant',
            'count',
            'refund_status',
            'final_price',
            'final_price_before_discount',
        )

    def get_variant_type(self, obj):
        return obj.product.id

    def get_product_id(self, obj):
        return obj.product.id

    def get_product_url(self, obj):
        return obj.product.get_absolute_url()

    def get_product_title_ir(self, obj):
        return obj.product.title_ir

    def get_product_title_en(self, obj):
        return obj.product.title_en

    def get_product_image(self, obj):
        return obj.product.image.name

    def get_refund_status(self, obj):
        return obj.refund.status


class OrderDetailSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    total_price_before_discount = serializers.SerializerMethodField()

    shipping_rate = serializers.SerializerMethodField()
    shipping_service = serializers.SerializerMethodField()

    address = OrderAddressSerializer()
    items = UserPaidOrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'status',
            'transaction',
            'tracking_code',
            'ordered_date',
            'shipped_date',
            'delivered_date',
            'total_price',
            'total_profit',
            'total_price_before_discount',
            'shipping_rate',

            'shipping_service',
            'address',
            'items',
        )

    def get_total_price(self, obj):
        return obj.get_total_price

    def get_total_profit(self, obj):
        return obj.get_total_profit

    def get_total_price_before_discount(self, obj):
        return obj.get_total_price_before_discount

    def get_shipping_rate(self, obj):
        return obj.shipping_effect_price if obj.shipping_effect_price else 0

    def get_shipping_service(self, obj):
        return {
            "image": obj.shipping.shipping_service.image.name,
            "name": obj.shipping.shipping_service.name
        }

    def get_transaction_id(self, obj):
        transaction = Transaction.objects.get_success().filter(order_id=obj.id).first()
        return transaction.transaction_id
