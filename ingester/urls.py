from django.conf.urls import url
from .models import local_url
from django.views.generic import ListView
from . import views
from .views import PublicationDetailView
#der namespace
app_name = 'ingester'


urlpatterns = [
    url(r'^ingester/(?P<config_id>[0-9]+)/log/$', views.log, name='config_log'),
    url(r'publications/$', ListView.as_view(paginate_by=50,
                                            model=local_url,
                                            queryset=local_url.objects.filter(global_url__id=1).select_related().all(),
                                            context_object_name="object_list",
                                            template_name='ingester/url_list.html',),name='bla'),
    url(r'search/$', views.search,name='search'),
    url(r'^(?P<pk>[0-9]+)/$', PublicationDetailView.as_view(), name='publication-detail'),
]
