from django.conf import settings
from django.db import models


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.label} - {self.address_line_1}, {self.address_line_2}, "
            f"{self.city}, {self.state}, {self.postal_code}, {self.country} "
            f"(User: {self.user.username})"
        )




class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/')
    is_active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Category: {self.name}, Description: {self.description}, Active: {self.is_active}, Parent: {self.parent}"



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




class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart (User: {self.user.username}) - Created: {self.created_at}"




class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_item_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.quantity} x {self.store_item.product.name} "
            f"@ {self.unit_price} (Total: {self.total_item_price}, Discount: {self.total_discount})"
        )




class Order(models.Model):
    STATUS_CHOICES = [
        (1, 'Pending'),
        (2, 'Processing'),
        (3, 'Delivered'),
        (4, 'Cancelled'),
        (5, 'Failed')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status_display = dict(self.STATUS_CHOICES).get(self.status, "Unknown")
        return (
            f"Order #{self.pk} (User: {self.user.username}), Status: {status_display}, "
            f"Address: {self.address}, Total: {self.total_price}"
        )




class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    store_item = models.ForeignKey(StoreItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return (
            f"{self.quantity} x {self.store_item.product.name} "
            f"at {self.store_item.price} (Total: {self.total_price})"
        )



class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=100)
    card_pan = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Payment for Order #{self.order.id}, TxID: {self.transaction_id}, "
            f"Amount: {self.amount}, Fee: {self.fee}, Status: {self.status}"
        )




class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        target = self.product.name if self.product else self.store.name
        return f"Review by {self.user.username} on {target} — Rating: {self.rating}"

