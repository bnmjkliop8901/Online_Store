from django.contrib import admin
from .models import Customer, Address

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'is_seller', 'is_staff']
    list_filter = ['is_seller', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['label', 'user', 'city', 'state', 'postal_code', 'country']
    search_fields = ['label', 'city', 'state', 'postal_code', 'country']
    autocomplete_fields = ['user']
