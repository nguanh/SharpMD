from django.conf.urls import url
from .models import local_url
from django.views.generic import ListView
from . import views
from .views import PublicationDetailView
#der namespace
app_name = 'ingester'


urlpatterns = [
    url(r'^ingester/(?P<config_id>[0-9]+)/log/$', views.log, name='config_log'),
    url(r'publications/$', views.search, name='search'),
    url(r'^(?P<pk>[0-9]+)/$', PublicationDetailView.as_view(), name='publication-detail'),
    url(r'^(?P<object_id>[0-9]+)/vote/(?P<attribute>[a-z_]+)$', views.vote, name='vote'),
]
