from .models import *
import django_filters

class PublicationFilter(django_filters.FilterSet):
    authors__block_name = django_filters.CharFilter(lookup_expr='icontains', label="Author")
    publication__title  = django_filters.CharFilter(lookup_expr='icontains', label="Title")
    class Meta:
        model = local_url
        fields = ['publication__title','authors__block_name']


class AuthorFilter(django_filters.FilterSet):
    block_name = django_filters.CharFilter(lookup_expr='icontains', label="Author")
    class Meta:
        model = local_url
        fields = ['block_name']
