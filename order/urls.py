from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CartViewSet, CartItemViewSet,
    OrderViewSet, OrderItemViewSet,
    PaymentViewSet, verify_payment,
    SellerStoreItemViewSet, SellerOrderViewSet
)


router = DefaultRouter()


router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)

#seller dashboard
router.register(r'seller/items', SellerStoreItemViewSet, basename='seller-items')
router.register(r'seller/orders', SellerOrderViewSet, basename='seller-orders')


urlpatterns = [
    path('', include(router.urls)),
    path('payments/verify/', verify_payment, name='verify-payment'),
]




