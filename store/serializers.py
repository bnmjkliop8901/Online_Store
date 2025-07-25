from rest_framework import serializers
from django.db.models import Min, Count
from .models import Category, Product, ProductImage, Store, StoreItem, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = '__all__'


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'


class StoreItemBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreItem
        fields = ['id', 'store', 'price', 'discount_price', 'stock', 'is_active']



class ProductWriteSerializer(serializers.ModelSerializer):
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all()
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'rating',
            'is_active', 'categories'
        ]


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    best_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'rating',
            'is_active', 'categories', 'images', 'best_price'
        ]

    def get_best_price(self, obj):
        discount = obj.storeitem_set.filter(is_active=True).aggregate(Min('discount_price'))['discount_price__min']
        if discount:
            return discount
        return obj.storeitem_set.filter(is_active=True).aggregate(Min('price'))['price__min']
        

class ProductDetailSerializer(ProductSerializer):
    sellers = serializers.SerializerMethodField()
    category_path = serializers.SerializerMethodField()
    best_seller = serializers.SerializerMethodField()

    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields + [
            'sellers', 'category_path', 'best_seller'
        ]

    def get_sellers(self, obj):
        items = obj.storeitem_set.select_related("store").filter(is_active=True, stock__gt=0)
        return StoreItemBasicSerializer(items, many=True).data

    def get_category_path(self, obj):
        categories = obj.categories.all()
        def depth(cat):
            count = 0
            while cat.parent:
                cat = cat.parent
                count += 1
            return count

        deepest = max(categories, key=depth, default=None)
        path = []
        while deepest:
            path.append({"id": deepest.id, "name": deepest.name})
            deepest = deepest.parent
        return path[::-1]


    def get_best_seller(self, obj):
        top_item = (
            obj.storeitem_set
            .annotate(order_count=Count('orderitem'))
            .filter(order_count__gt=0)
            .order_by('-order_count')
            .first()
        )
        if top_item:
            return StoreItemBasicSerializer(top_item).data
        return None



class StoreItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )
    store = serializers.PrimaryKeyRelatedField(
        queryset=Store.objects.all()
    )

    class Meta:
        model = StoreItem
        fields = '__all__'
    def validate(self, data):
        price = data.get('price')
        discount_price = data.get('discount_price')
        if discount_price is not None and discount_price > price:
            raise serializers.ValidationError({
                "discount_price": "Discount price must be less than or equal to the regular price."
            })
        return data

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class CategoryTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'children']

    def get_children(self, obj):
        children = Category.objects.filter(parent=obj, is_active=True)
        return CategoryTreeSerializer(children, many=True).data
