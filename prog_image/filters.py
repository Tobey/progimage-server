from uuid import UUID

import django_filters
from django_filters.fields import Lookup
from rest_framework.exceptions import ValidationError


class ListFilter(django_filters.Filter):
    def filter(self, qs, value):
        if not value:
            return qs

        uuids = value.split(',')
        try:
            [UUID(u, version=4) for u in uuids]
        except:
            raise ValidationError('invalid UUID given as filter')
        return qs.filter(id__in=uuids)


class ImageFilter(django_filters.FilterSet):
    id__in = ListFilter(field_name='id')
