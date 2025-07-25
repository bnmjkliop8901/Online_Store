from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import (
    CategoryViewSet,
    ProductViewSet,
    ProductImageViewSet,
    StoreViewSet,
    StoreItemViewSet,
    ReviewViewSet,
    category_tree_view,
    SellerStoreItemViewSet,
    SellerStoreViewSet,
    SellerProductViewSet,
    SellerCategoryViewSet
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'product-images', ProductImageViewSet)
router.register(r'stores', StoreViewSet)
router.register(r'store-items', StoreItemViewSet)
router.register(r'reviews', ReviewViewSet)

router.register(r'seller/stores', SellerStoreViewSet, basename='seller-stores')
router.register(r'seller/products', SellerProductViewSet, basename='seller-products')
router.register(r'seller/categories', SellerCategoryViewSet, basename='seller-categories')



urlpatterns = [
    path('category-tree/', category_tree_view, name='category-tree'),
] + router.urls
