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
            'id', 'store_item', 'quantity',
            'unit_price', 'total_item_price', 'total_discount'
        ]
        read_only_fields = ['unit_price', 'total_item_price', 'total_discount']

    def validate(self, data):
        store_item = data['store_item']
        quantity = data['quantity']
        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)

        existing_quantity = cart.items.filter(store_item=store_item).aggregate(
            total=serializers.models.Sum('quantity')
        )['total'] or 0

        total_requested = existing_quantity + quantity
        if total_requested > store_item.stock:
            raise serializers.ValidationError(
                f"Total requested ({total_requested}) exceeds stock ({store_item.stock})"
            )

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        cart, _ = Cart.objects.get_or_create(user=user)
        store_item = validated_data['store_item']
        quantity = validated_data['quantity']

        unit_price = store_item.discount_price or store_item.price
        total_price = unit_price * quantity
        discount_per_unit = (
            store_item.price - unit_price if store_item.discount_price else 0
        )
        total_discount = discount_per_unit * quantity

        return CartItem.objects.create(
            cart=cart,
            store_item=store_item,
            quantity=quantity,
            unit_price=unit_price,
            total_item_price=total_price,
            total_discount=total_discount
        )




class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'created_at', 'items', 'total_price', 'total_discount']

    def get_total_price(self, obj):
        return sum(item.total_item_price for item in obj.items.all())

    def get_total_discount(self, obj):
        return sum(item.total_discount for item in obj.items.all())




class OrderItemSerializer(serializers.ModelSerializer):
    store_item = StoreItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['store_item', 'quantity', 'price', 'total_price']
        

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    address = AddressSerializer(read_only=True)
    user = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


    class Meta:
        model = Order
        fields = [
            'id', 'user', 'address', 'status', 'status_display',
            'total_price', 'created_at', 'updated_at', 'order_items'
        ]

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_user(self, obj):
        return {
            "id": obj.user.id,
            "name": obj.user.get_full_name()
        }


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = 'all'




























































# from rest_framework import serializers
# from .models import Cart, CartItem, Order, OrderItem, Payment
# from store.serializers import StoreItemSerializer
# from customer.serializers import AddressSerializer
# from store.models import StoreItem




# class CartItemSerializer(serializers.ModelSerializer):
#     store_item = serializers.PrimaryKeyRelatedField(queryset=StoreItem.objects.all())

#     class Meta:
#         model = CartItem
#         fields = [
#             'id', 'store_item', 'quantity',
#             'unit_price', 'total_item_price', 'total_discount'
#         ]
#         read_only_fields = ['unit_price', 'total_item_price', 'total_discount']

#     def validate(self, data):
#         store_item = data['store_item']
#         quantity = data['quantity']
#         user = self.context['request'].user
#         cart, _ = Cart.objects.get_or_create(user=user)

#         existing_quantity = cart.items.filter(store_item=store_item).aggregate(
#             total=serializers.models.Sum('quantity')
#         )['total'] or 0

#         total_requested = existing_quantity + quantity
#         if total_requested > store_item.stock:
#             raise serializers.ValidationError(
#                 f"Total requested ({total_requested}) exceeds stock ({store_item.stock})"
#             )

#         return data

# def create(self, validated_data):
#     user = self.context['request'].user
#     cart, _ = Cart.objects.get_or_create(user=user, is_active=True)  # ✅ only one active cart

#     store_item = validated_data['store_item']
#     quantity = validated_data['quantity']

#     unit_price = store_item.discount_price or store_item.price
#     total_price = unit_price * quantity
#     discount_per_unit = (
#         store_item.price - unit_price if store_item.discount_price else 0
#     )
#     total_discount = discount_per_unit * quantity

#     return CartItem.objects.create(
#         cart=cart,
#         store_item=store_item,
#         quantity=quantity,
#         unit_price=unit_price,
#         total_item_price=total_price,
#         total_discount=total_discount
#     )





# class CartSerializer(serializers.ModelSerializer):
#     items = CartItemSerializer(many=True, read_only=True)
#     total_price = serializers.SerializerMethodField()
#     total_discount = serializers.SerializerMethodField()

#     class Meta:
#         model = Cart
#         fields = ['id', 'user', 'created_at', 'items', 'total_price', 'total_discount']

#     def get_total_price(self, obj):
#         return sum(item.total_item_price for item in obj.items.all())

#     def get_total_discount(self, obj):
#         return sum(item.total_discount for item in obj.items.all())




# class OrderItemSerializer(serializers.ModelSerializer):
#     store_item = StoreItemSerializer(read_only=True)

#     class Meta:
#         model = OrderItem
#         fields = ['store_item', 'quantity', 'price', 'total_price']
        

# class OrderSerializer(serializers.ModelSerializer):
#     order_items = OrderItemSerializer(many=True, read_only=True)
#     address = AddressSerializer(read_only=True)
#     user = serializers.SerializerMethodField()
#     status_display = serializers.SerializerMethodField()
#     total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


#     class Meta:
#         model = Order
#         fields = [
#             'id', 'user', 'address', 'status', 'status_display',
#             'total_price', 'created_at', 'updated_at', 'order_items'
#         ]

#     def get_status_display(self, obj):
#         return obj.get_status_display()

#     def get_user(self, obj):
#         return {
#             "id": obj.user.id,
#             "name": obj.user.get_full_name()
#         }


# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         fields = '__all__'
