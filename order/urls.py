from rest_framework.routers import DefaultRouter
from .views import (
    CartViewSet, CartItemViewSet,
    OrderViewSet, OrderItemViewSet,
    PaymentViewSet
)

router = DefaultRouter()
router.register(r'carts', CartViewSet)
router.register(r'cart-items', CartItemViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = router.urls
