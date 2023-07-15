from rest_framework import serializers

from site_shop.order_management.models import OrderAddress, OrderItem, Order
from site_shop.product_management.serializers import VariantTypeSerializer, ProductVariantSerializer
from site_shop.shipping_management.serializers import ShippingRateSerializer
from site_shop.transaction_management.models import TransactionStatus
from site_utils.persian.date import model_date_field_convertor


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


class CurrentOpenOrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    shipping = ShippingRateSerializer()

    class Meta:
        model = Order
        fields = (
            'id',
            'items',
            'shipping'
        )

    def get_items(self, obj: Order):
        items = obj.items.filter(variant__is_active=True, product__is_active=True)
        serializer = CurrentOrderItemSerializer(items, many=True)
        return serializer.data


class CurrentPendingOrderSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    repayment_date_expire = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'slug',
            'price',
            'repayment_date_expire',
            'items',
        )

    def get_items(self, obj: Order):
        items = obj.items.filter(variant__is_active=True, product__is_active=True)
        serializer = CurrentOrderItemSerializer(items, many=True)
        return serializer.data

    def get_price(self, obj: Order):
        return obj.get_payment_price

    def get_repayment_date_expire(self, obj: Order):
        return model_date_field_convertor(obj.repayment_date_expire)


class CurrentOrderSerializer(serializers.Serializer):
    open = CurrentOpenOrderSerializer()
    pending = CurrentPendingOrderSerializer(many=True)


# Order , Item Serializer ( Paid )
class UserPaidOrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.SerializerMethodField()
    product_url = serializers.SerializerMethodField()
    product_title_ir = serializers.SerializerMethodField()
    product_title_en = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    is_special = serializers.SerializerMethodField()
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
            'is_special',
            'final_price',
            'final_price_before_discount',
            'final_discount',
            'final_profit',
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

    def get_is_special(self, obj):
        return obj.variant.is_special

    def get_refund_status(self, obj: OrderItem):
        return obj.refund.status if obj.refund else None


class UserPaidOrderSerializer(serializers.ModelSerializer):
    total_payment_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_profit = serializers.SerializerMethodField()
    total_profit_before_discount = serializers.SerializerMethodField()
    total_price_before_discount = serializers.SerializerMethodField()

    shipping_service = serializers.SerializerMethodField()

    address = OrderAddressSerializer()
    items = UserPaidOrderItemSerializer(many=True)
    transaction_id = serializers.SerializerMethodField()
    repayment_date_expire = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'slug',
            'transaction_id',
            'tracking_code',

            'delivery_status',
            'payment_status',

            'date_delivery_status_updated',
            'date_ordered',
            'date_shipped',
            'date_delivered',

            'total_payment_price',
            'total_price',
            'total_profit',
            'total_profit_before_discount',
            'total_price_before_discount',

            'coupon_effect_price',
            'repayment_date_expire',
            'shipping_service',
            'address',
            'items',
        )

    def get_repayment_date_expire(self, obj: Order):
        return model_date_field_convertor(obj.repayment_date_expire)

    def get_total_payment_price(self, obj):
        return obj.get_payment_price

    def get_total_price(self, obj):
        return obj.get_total_price

    def get_total_profit(self, obj):
        return obj.get_user_total_profit

    def get_total_profit_before_discount(self, obj):
        return obj.get_user_total_profit_before_discount

    def get_total_price_before_discount(self, obj):
        return obj.get_total_price_before_discount

    def get_shipping_service(self, obj: Order):
        return {
            "image": obj.shipping.shipping_service.image.name,
            "name": obj.shipping.shipping_service.name,
            "price": obj.shipping_effect_price,
            "pay_at_destination": obj.shipping.pay_at_destination,
        }

    def get_transaction_id(self, obj: Order):
        transaction = obj.transactions.filter(is_delete=False, status=TransactionStatus.SUCCESS.name).first()
        if transaction:
            return transaction.transaction_id

        return None
