from django.conf.urls import url
from .views import PublicationList
from .models import publication, local_url
from django.views.generic import ListView
from . import views
#der namespace
app_name = 'ingester'


urlpatterns = [
    url(r'^ingester/(?P<config_id>[0-9]+)/log/$', views.log, name='config_log'),
    url(r'publications/$', ListView.as_view(paginate_by=50,
                                            model=local_url,
                                            queryset=publication.objects.all(),
                                            context_object_name="object_list",
                                            template_name='ingester/publication_list.html',)),
]
