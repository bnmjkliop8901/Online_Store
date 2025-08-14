from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_seller = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False) # for soft delete

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save()

    def hard_delete(self, request_user):
        if request_user.is_staff or request_user.is_superuser:
            super().delete()
        else:
            raise PermissionError("You do not have permission to hard delete.")


    def __str__(self):
        return (
            f"Username: {self.username}, Email: {self.email}, "
            f"Phone: {self.phone}, Seller: {self.is_seller}, Staff: {self.is_staff}"
        )


class Address(models.Model):
    user = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses') # for accessing all user's addressess (user.addresses)
    label = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def hard_delete(self, request_user):
        if request_user.is_staff or request_user.is_superuser:
            super().delete()
        else:
            raise PermissionError("You do not have permission to hard delete.")

    def __str__(self):
        return (
            f"{self.label} - {self.address_line_1}, {self.address_line_2}, "
            f"{self.city}, {self.state}, {self.postal_code}, {self.country} "
            f"(User: {self.user.username})"
        )
