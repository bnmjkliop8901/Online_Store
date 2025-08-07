from django.db import models
from django.conf import settings
from store.models import StoreItem, Product, Store
from customer.models import Address

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
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
    PAYMENT_STATUS_CHOICES = [
    (1, 'Pending'),
    (2, 'Verified'),
    (3, 'Failed'),
    (4, 'Refunded'),
]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=100)
    reference_id = models.CharField(max_length=100)
    card_pan = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.PositiveSmallIntegerField(choices=PAYMENT_STATUS_CHOICES,default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"Payment for Order #{self.order.id}, TxID: {self.transaction_id}, "
            f"Amount: {self.amount}, Fee: {self.fee}, Status: {self.status}"
        )
