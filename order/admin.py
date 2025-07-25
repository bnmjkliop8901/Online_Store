from django.contrib import admin
from rest_framework.exceptions import ValidationError
from .models import Cart, CartItem, Order, OrderItem, Payment

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    search_fields = ['user__username']
    autocomplete_fields = ['user']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'store_item', 'quantity', 'unit_price', 'total_item_price', 'total_discount']
    list_filter = ['cart']
    search_fields = ['store_item__product__name']
    autocomplete_fields = ['cart', 'store_item']
    readonly_fields = ['unit_price', 'total_item_price', 'total_discount']

    def save_model(self, request, obj, form, change):
        item = obj.store_item
        quantity = obj.quantity

        if quantity > item.stock:
            raise ValidationError(
                f"Cannot add {quantity} items. Only {item.stock} units available in stock."
            )

        unit_price = item.discount_price or item.price
        total_price = unit_price * quantity
        discount_per_unit = (item.price - unit_price) if item.discount_price else 0
        total_discount = discount_per_unit * quantity

        obj.unit_price = unit_price
        obj.total_item_price = total_price
        obj.total_discount = total_discount

        # ✅ Deduct stock only if creating a new item
        if not change:
            item.stock = max(item.stock - quantity, 0)
            item.save(update_fields=["stock"])

        super().save_model(request, obj, form, change)




@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username']
    autocomplete_fields = ['user', 'address']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'store_item', 'quantity', 'price', 'total_price']
    search_fields = ['store_item__product__name']
    autocomplete_fields = ['order', 'store_item']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'transaction_id', 'amount', 'fee', 'status', 'created_at']
    search_fields = ['transaction_id', 'reference_id']
    autocomplete_fields = ['order']