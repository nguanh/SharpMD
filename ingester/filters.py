from .models import *
import django_filters

class PublicationFilter(django_filters.FilterSet):
    class Meta:
        model = local_url
        fields = ['publication__title','authors__block_name']

