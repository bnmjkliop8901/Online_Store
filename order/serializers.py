from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from store.serializers import StoreItemSerializer
from customer.serializers import AddressSerializer
from store.models import StoreItem



class CartItemSerializer(serializers.ModelSerializer):
    store_item = serializers.PrimaryKeyRelatedField(queryset=StoreItem.objects.all())

    class Meta:
        model = CartItem
        fields = [
            'store_item', 'quantity',
            'unit_price', 'total_item_price', 'total_discount'
        ]
        read_only_fields = ['unit_price', 'total_item_price', 'total_discount']

    def validate(self, data):
        store_item = data['store_item']
        quantity = data['quantity']

        if quantity > store_item.stock:
            raise serializers.ValidationError(
                f"Only {store_item.stock} units in stock, but you requested {quantity}."
            )
        return data

    def create(self, validated_data):
        store_item = validated_data['store_item']
        quantity = validated_data['quantity']

        # Backup validation in case DRF skips validate()
        if quantity > store_item.stock:
            raise serializers.ValidationError("Requested quantity exceeds available stock.")

        unit_price = store_item.discount_price or store_item.price
        total_price = unit_price * quantity
        discount_per_unit = (store_item.price - unit_price) if store_item.discount_price else 0
        total_discount = discount_per_unit * quantity

        return CartItem.objects.create(
            store_item=store_item,
            quantity=quantity,
            unit_price=unit_price,
            total_item_price=total_price,
            total_discount=total_discount,
            user=self.context['request'].user
        )




class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    store_item = StoreItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'address', 'status', 'total_price', 'created_at', 'updated_at', 'items']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
