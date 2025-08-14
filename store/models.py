from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    # def __str__(self):
        # return f"Category: {self.name}, Description: {self.description}, Active: {self.is_active}, Parent: {self.parent}"
    def __str__(self):
        parent_name = self.parent.name if self.parent else "None"
        return f"Category: {self.name}, Parent: {parent_name}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, related_name='products')

    def __str__(self):
        return f"Product: {self.name}, Rating: {self.rating}, Active: {self.is_active}, Categories: {[c.name for c in self.categories.all()]}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"ProductImage for {self.product.name}, URL: {self.image.url}"


class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stores')

    def __str__(self):
        return f"Store: {self.name}, Description: {self.description}, Seller: {self.seller.username}"


class StoreItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.product.name} at {self.store.name}, Price: {self.price}, "
            f"Discount: {self.discount_price}, Stock: {self.stock}, Active: {self.is_active}"
        )



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey('Store', on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.product.name if self.product else self.store.name
        return f"Review by {self.user.username} on {target} — Rating: {self.rating}"
