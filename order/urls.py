from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CartViewSet, CartItemViewSet,
    OrderViewSet, OrderItemViewSet,
    PaymentViewSet, verify_payment,
    SellerStoreItemViewSet, SellerOrderViewSet,





    # MyCartView, CartItemsView,
    # AddToCartView, UpdateCartItemView,
    # RemoveCartItemView,
)


router = DefaultRouter()


# router.register(r'carts', CartViewSet, basename='cart')
router.register(r'mycart', CartViewSet, basename='cart')
router.register(r'mycart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)

#seller dashboard
router.register(r'seller/items', SellerStoreItemViewSet, basename='seller-items')
router.register(r'seller/orders', SellerOrderViewSet, basename='seller-orders')



urlpatterns = [
    path('', include(router.urls)),
    path('payments/verify/', verify_payment, name='verify-payment'),





    # path("mycart/", MyCartView.as_view(), name="mycart"),
    # path("mycart/items/", CartItemsView.as_view(), name="mycart-items"),
    # path("mycart/add_to_cart/<int:id>/", AddToCartView.as_view(), name="add-to-cart"),
    # path("mycart/items/<int:id>/", UpdateCartItemView.as_view(), name="update-cart-item"),
    # path("mycart/items/<int:id>/", RemoveCartItemView.as_view(), name="remove-cart-item"), 
]
