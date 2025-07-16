from rest_framework import viewsets
from .models import Category, Product, ProductImage, Store, StoreItem, Review
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, StoreSerializer, StoreItemSerializer, ReviewSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('categories', 'images')
    serializer_class = ProductSerializer

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class StoreItemViewSet(viewsets.ModelViewSet):
    queryset = StoreItem.objects.select_related('store', 'product')
    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product', 'store')
    serializer_class = ReviewSerializer
