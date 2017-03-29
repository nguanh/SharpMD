from django.conf.urls import url

from . import views
#der namespace
app_name = 'ingester'


urlpatterns = [
    url(r'^ingester/(?P<config_id>[0-9]+)/log/$', views.log, name='config_log'),
]
