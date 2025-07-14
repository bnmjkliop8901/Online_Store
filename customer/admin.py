from django.contrib import admin
from customer.models import Customer

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone', 'is_seller', 'is_staff']
    list_filter = ['is_seller', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'phone']
