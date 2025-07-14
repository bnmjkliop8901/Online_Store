from django.contrib import admin
from store.models import (
    Address, Category, Product, ProductImage, Store,
    StoreItem, Cart, CartItem, Order, OrderItem, Payment, Review
)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'rating', 'is_active']
    list_filter = ['is_active', 'categories']
    search_fields = ['name', 'description']
    autocomplete_fields = ['categories']

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    search_fields = ['product__name']
    autocomplete_fields = ['product']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'parent']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    autocomplete_fields = ['parent']

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller']
    search_fields = ['name', 'seller__username']
    autocomplete_fields = ['seller']

@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'price', 'discount_price', 'stock', 'is_active']
    list_filter = ['store', 'is_active']
    search_fields = ['product__name', 'store__name']
    list_editable = ['price', 'discount_price', 'stock']
    autocomplete_fields = ['product', 'store']

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

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['label', 'user', 'city', 'state', 'postal_code', 'country']
    search_fields = ['label', 'city', 'state', 'postal_code', 'country']
    autocomplete_fields = ['user']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'transaction_id', 'amount', 'fee', 'status', 'created_at']
    search_fields = ['transaction_id', 'reference_id']
    autocomplete_fields = ['order']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'store', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'store__name']
    autocomplete_fields = ['user', 'product', 'store']
