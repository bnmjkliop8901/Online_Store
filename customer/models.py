from django.contrib.auth.models import AbstractUser
from django.db import models


class Customer(AbstractUser):
    phone = models.CharField(max_length=20, null=True, blank=True)
    picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    is_seller = models.BooleanField(default=False)

    def __str__(self):
        return self.username
