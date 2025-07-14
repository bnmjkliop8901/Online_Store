from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, ProductViewSet, ProductImageViewSet,
    StoreViewSet, StoreItemViewSet, ReviewViewSet
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'store-items', StoreItemViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = router.urls
