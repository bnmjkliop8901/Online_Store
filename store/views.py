from rest_framework import viewsets , status
from rest_framework.permissions import IsAuthenticatedOrReadOnly , IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from store.models import Category, Product, ProductImage, Store, StoreItem, Review
from store.serializers import (
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
from store.filters import ProductFilter
from store.permissions import IsSeller
from rest_framework.decorators import api_view , action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer 

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSeller()]
        return [IsAuthenticatedOrReadOnly()]

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


# class ProductViewSet(viewsets.ModelViewSet):
#     queryset = Product.objects.prefetch_related('categories', 'images').order_by('id')
#     filterset_class = ProductFilter
#     filter_backends = [DjangoFilterBackend]

#     def get_serializer_class(self):
#         if self.action in ['create', 'update', 'partial_update']:
#             return ProductWriteSerializer
#         if self.action == 'retrieve':
#             return ProductDetailSerializer
#         return ProductSerializer



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

    @action(detail=True, methods=['get'], url_path='review_list')
    def review_list(self, request, pk=None):
        product = self.get_object()
        reviews = Review.objects.filter(product=product).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = request.query_params.get('page_size', 5)
        paginated_reviews = paginator.paginate_queryset(reviews, request)

        serializer = ReviewSerializer(paginated_reviews, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='review_create', permission_classes=[IsAuthenticated])
    def review_create(self, request, pk=None):
        product = self.get_object()
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    

    @action(detail=False, methods=['get', 'put'], url_path='me')
    def my_store(self, request):
        store = Store.objects.filter(seller=request.user).first()
        if not store:
            return Response({"detail": "Store not found."}, status=404)

        if request.method == 'GET':
            serializer = self.get_serializer(store)
            return Response(serializer.data)

        # PUT request
        serializer = self.get_serializer(store, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# class StoreItemViewSet(viewsets.ModelViewSet):
#     queryset = StoreItem.objects.select_related('store', 'product')
#     serializer_class = StoreItemSerializer
class StoreItemViewSet(viewsets.ModelViewSet):
    serializer_class = StoreItemSerializer

    def get_queryset(self):
        return StoreItem.objects.filter(store__seller=self.request.user)


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.select_related('user', 'product', 'store')
    serializer_class = ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        return Product.objects.filter(storeitem__store__seller=self.request.user).distinct()

    # def perform_create(self, serializer):
    #     product = serializer.save()
    #     StoreItem.objects.create(
    #         product=product,
    #         store=self.request.user.stores.first(),
    #         price=0,
    #         stock=0,
    #         is_active=False
    #     )
    def perform_create(self, serializer):
        serializer.save()


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
