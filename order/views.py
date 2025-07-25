from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer
from rest_framework.permissions import IsAuthenticated

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.prefetch_related('items')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.select_related('store_item', 'cart')
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        cart = Cart.objects.get(user=user)

        # Optional: validate cart is not empty
        if not cart.items.exists():
            raise ValidationError("Your cart is empty.")

        # Loop through items and update stock
        for item in cart.items.select_related('store_item'):
            if item.quantity > item.store_item.stock:
                raise ValidationError(
                    f"Insufficient stock for {item.store_item.product.name}. Only {item.store_item.stock} left."
                )

        order = serializer.save(user=user)

        # Create order items and update stock
        for item in cart.items.select_related('store_item'):
            OrderItem.objects.create(
                order=order,
                store_item=item.store_item,
                quantity=item.quantity,
                price=item.unit_price,
                total_price=item.total_item_price
            )
            store_item = item.store_item
            store_item.stock = max(store_item.stock - item.quantity, 0)
            store_item.save(update_fields=["stock"])


        # Optional: clear cart
        cart.items.all().delete()


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.select_related('store_item', 'order')
    serializer_class = OrderItemSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('order')
    serializer_class = PaymentSerializer
