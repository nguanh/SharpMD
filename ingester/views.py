from __future__ import absolute_import, unicode_literals
from django.shortcuts import get_object_or_404, render
from .models import Config, local_url
from .filters import PublicationFilter
from django.views.generic.detail import DetailView
from .difference_storage import deserialize_diff_store
import os
import tailer


# Create your views here.
PROJECT_DIR = os.path.dirname(__file__)


def log(request, config_id):
    config = get_object_or_404(Config, pk=config_id)
    log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
    log_name = config.name.strip().replace(" ", "_")
    log_file = os.path.join(log_dir, "{}.log").format(log_name)
    log_exists = os.path.isfile(os.path.join(log_file))
    if log_exists:
        with open(log_file, 'r') as f:
            log_text = "\n".join(tailer.tail(f, 40))
    else:
        log_text = "No log found!"

    return render(request, 'harvester/admin_log.html',{
            'harvester_name': config.name,
            'log_text': log_text,
    })


def search(request):
    qs = local_url.objects.filter(global_url__id=1).all()
    if 'publication__title' in request.GET:
        if request.GET['publication__title'] == ['']:
            del request.GET['publication__title']

    if 'authors__block_name' in request.GET:
        if request.GET['authors__block_name'] == ['']:
            del request.GET['authors__block_name']
    url_filter = PublicationFilter(request.GET, queryset=qs)
    return render(request, 'ingester/search_list.html', {'filter': url_filter})


class PublicationDetailView(DetailView):
    model = local_url
    queryset = local_url.objects.filter(global_url__id=1).all()
    template_name = 'ingester/pub_details.html'

    def get_object(self, queryset=None):
        obj = super(PublicationDetailView,self).get_object(queryset)
        return obj

    def get_context_data(self, **kwargs):
        obj = super(PublicationDetailView, self).get_context_data(**kwargs)
        diff_tree = deserialize_diff_store(obj['object'].publication.differences)
        obj['diff_tree'] = diff_tree
        obj['test'] = 'pupsi'
        return obj


