import django_filters
from .models import *


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = {
            'brandname',
            'socket',
            'seriescpu',
            'memory_type',
            'capacity',
            'screensize',
            'resolution',
            'wattage',
        }
