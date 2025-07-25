import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['name', 'is_active']
