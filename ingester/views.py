from __future__ import absolute_import, unicode_literals
from django.shortcuts import get_object_or_404, render,render_to_response
from django.views.generic import ListView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Config, publication, local_url
from .filters import PublicationFilter
from search_listview.list import SearchableListView
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


