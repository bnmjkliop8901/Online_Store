from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly , IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, Store, StoreItem, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    StoreSerializer,
    StoreItemSerializer,
    ReviewSerializer,
    CategoryTreeSerializer,
    ProductWriteSerializer
)
from .filters import ProductFilter
from .permissions import IsSeller
from rest_framework.decorators import api_view
from rest_framework.response import Response


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSeller()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('categories', 'images').order_by('id')
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ProductWriteSerializer
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer

class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticatedOrReadOnly()]
        return [IsAuthenticated(), IsSeller()]
    
class StoreItemViewSet(viewsets.ModelViewSet):
    queryset = StoreItem.objects.select_related('store', 'product')
    serializer_class = StoreItemSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product', 'store')
    serializer_class = ReviewSerializer


class SellerStoreItemViewSet(viewsets.ModelViewSet):
    serializer_class = StoreItemSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return StoreItem.objects.filter(store__seller=self.request.user)

    def perform_create(self, serializer):
        store = self.request.user.stores.first()
        serializer.save(store=store)

class SellerStoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Store.objects.filter(seller=self.request.user)

    def perform_create(self, serializer):
        if not getattr(self.request.user, 'is_seller', False):
            raise PermissionDenied("Only sellers can create stores.")
        serializer.save(seller=self.request.user)



class SellerProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductWriteSerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Product.objects.filter(
            storeitem__store__seller=self.request.user
        ).distinct()

    def perform_create(self, serializer):
        product = serializer.save()
        StoreItem.objects.create(
            product=product,
            store=self.request.user.stores.first(),
            price=0,
            stock=0,
            is_active=False
        )


class SellerCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsSeller]

    def get_queryset(self):
        return Category.objects.filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save()



@api_view(['GET'])
def category_tree_view(request):
    top_categories = Category.objects.filter(parent=None, is_active=True)
    serializer = CategoryTreeSerializer(top_categories, many=True)
    return Response(serializer.data)
