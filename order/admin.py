from django.contrib import admin
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