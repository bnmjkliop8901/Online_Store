from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Customer, Address


@admin.register(Customer)
class CustomerAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('phone', 'is_seller', 'is_deleted')}),)
    list_display = [
        'username', 'email', 'phone',
        'is_seller', 'is_staff', 'is_active',
        'is_deleted'
    ]
    list_filter = ['is_seller', 'is_staff', 'is_superuser', 'is_deleted']
    search_fields = ['username', 'email', 'phone']
    actions = ['restore_customer']

    @admin.action(description="Restore selected customers")
    def restore_customer(self, request, queryset):
        queryset.update(is_deleted=False, is_active=True)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'label', 'user', 'city', 'state',
        'postal_code', 'country', 'is_deleted'
    ]
    list_filter = ['is_deleted']
    search_fields = ['label', 'city', 'state', 'postal_code', 'country']
    autocomplete_fields = ['user']
    actions = ['restore_address']

    @admin.action(description="Restore selected addresses")
    def restore_address(self, request, queryset):
        queryset.update(is_deleted=False)
