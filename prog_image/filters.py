import django_filters
from django_filters.fields import Lookup


class ListFilter(django_filters.Filter):
    def filter(self, qs, value):
        return super().filter(qs, Lookup(value.split(','), 'in'))


class ImageFilter(django_filters.FilterSet):
    image__in = ListFilter(name='id')
