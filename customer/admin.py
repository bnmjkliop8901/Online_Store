from django.contrib import admin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.template.response import TemplateResponse
from django.urls import path
from django.shortcuts import redirect
from django.utils.html import format_html
from .models import Customer, Address


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'phone',
        'is_seller', 'is_staff', 'is_active',
        'is_deleted', 'change_password_link'
    ]
    list_filter = ['is_seller', 'is_staff', 'is_superuser', 'is_deleted']
    search_fields = ['username', 'email', 'phone']
    actions = ['restore_customer']


    def get_queryset(self, request):
        return super().get_queryset(request)


    def change_password_link(self, obj):
        return format_html('<a href="password/{}/">Change Password</a>', obj.pk)
    change_password_link.short_description = 'Password'


    @admin.action(description="Restore selected customers")
    def restore_customer(self, request, queryset):
        queryset.update(is_deleted=False, is_active=True)


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'password/<int:user_id>/',
                self.admin_site.admin_view(self.change_user_password),
                name='customer_change_password',
            ),
        ]
        return custom_urls + urls

    def change_user_password(self, request, user_id):
        user = self.get_object(request, user_id)
        form = AdminPasswordChangeForm(user, request.POST or None)

        if form.is_valid():
            form.save()
            self.message_user(request, f"Password for '{user.username}' changed successfully.")
            return redirect(f'../../{user_id}/change/')

        context = {
            'title': f'Change password: {user.username}',
            'form': form,
            'original': user,
            'opts': self.model._meta,
            'save_as': False,
            'has_delete_permission': False,
            'has_add_permission': False,
            'has_change_permission': True,
        }

        return TemplateResponse(request, "admin/auth/user/change_password.html", context)


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


    def get_queryset(self, request):
        return super().get_queryset(request)

    @admin.action(description="Restore selected addresses")
    def restore_address(self, request, queryset):
        queryset.update(is_deleted=False)
