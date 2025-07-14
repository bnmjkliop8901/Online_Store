from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from store.serializers import StoreItemSerializer
from customer.serializers import AddressSerializer

class CartItemSerializer(serializers.ModelSerializer):
    store_item = StoreItemSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = '__all__'

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
