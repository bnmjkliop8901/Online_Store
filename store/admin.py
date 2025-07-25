from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Category, Product, ProductImage, Store, StoreItem, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'parent']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    autocomplete_fields = ['parent']

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

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller']
    search_fields = ['name', 'seller__username']
    autocomplete_fields = ['seller']

    def save_model(self, request, obj, form, change):
        if not getattr(request.user, 'is_seller', False):
            raise ValidationError("You must be a seller to create a store.")
        obj.seller = request.user
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        return getattr(request.user, 'is_seller', False)

@admin.register(StoreItem)
class StoreItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'price', 'discount_price', 'stock', 'is_active']
    list_filter = ['store', 'is_active']
    search_fields = ['product__name', 'store__name']
    list_editable = ['price', 'discount_price', 'stock']
    autocomplete_fields = ['product', 'store']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'store', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'product__name', 'store__name']
    autocomplete_fields = ['user', 'product', 'store']
