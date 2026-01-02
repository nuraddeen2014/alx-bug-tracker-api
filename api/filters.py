from django_filters.rest_framework import FilterSet
from .models import Tag


class BugPostFilter(FilterSet):
    class Meta:
        model = Tag
        fields = {
            'name': ['exact', 'icontains'],
        }