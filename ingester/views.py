from __future__ import absolute_import, unicode_literals
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from .difference_storage import deserialize_diff_store, get_sources, get_value_list, upvote, get_default_values, serialize_diff_store
from .models import Config, local_url, PubReference,authors_model, pub_medium, publication
from .filters import PublicationFilter,AuthorFilter
import os
import tailer
import datetime

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


def home_view(request):
    return render(request, 'ingester/base.html')


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


def author_search(request):
    qs = authors_model.objects.all()
    url_filter = AuthorFilter(request.GET, queryset=qs)
    return render(request, 'ingester/author_list.html', {'filter': url_filter})


class PublicationDetailView(DetailView):
    model = local_url
    queryset = local_url.objects.filter(global_url__id=1).all()
    template_name = 'ingester/pub_details.html'

    def get_object(self, queryset=None):
        obj = super(PublicationDetailView,self).get_object(queryset)
        return obj

    def get_context_data(self, **kwargs):
        obj = super(PublicationDetailView, self).get_context_data(**kwargs)
        # ===========================SOURCE VIEW =======================================================================
        diff_tree = deserialize_diff_store(obj['object'].publication.differences)
        obj['sources'] = get_sources(diff_tree)
        # resolve author ids into authors
        for element in obj['sources']:
            element['authors'] = authors_model.objects.filter(id__in=element['author_values']).all()
            del element['author_values']
        # resolve medium id
            if 'pub_source_ids' in element:
                element['medium'] = {'value': pub_medium.objects.get(id=element['pub_source_ids']['value']).main_name,
                                    'votes': element['pub_source_ids']['votes']
                                    }
        # TODO resolve keywords
        # ============================REFERENCE VIEW ==================================================================
        references =[x.reference.id for x in PubReference.objects.select_related('reference').filter(source=obj['local_url']).all()]
        ref_url_list = local_url.objects.filter(publication__cluster_id__in= references).all()
        obj['references'] = ref_url_list
        # cited by
        cluster = obj['local_url'].publication.cluster
        cited = [x.source for x in PubReference.objects.select_related('source').filter(reference=cluster).all()]
        obj['cites'] = cited
        # ============================EDIT VIEW=========================================================================
        obj['value_view'] = get_value_list(diff_tree)
        return obj


def vote(request, object_id,attribute):
    # get diff tree
    obj = get_object_or_404(local_url, pk=object_id)
    pub = obj.publication
    diff_tree = deserialize_diff_store(pub.differences)
    # upvote
    upvote(diff_tree, attribute, request.POST['choice'])
    # get new default values
    new_defaults = get_default_values(diff_tree)
    print(new_defaults)
    if 'date_published' in new_defaults and  new_defaults['date_published'] is not None:
        new_defaults['date_published'] = datetime.date(new_defaults["date_published"], 1, 1)
    new_defaults['differences'] = serialize_diff_store(diff_tree)

    for key, value in new_defaults.items():
        setattr(pub, key, value)
    pub.save()
    return HttpResponseRedirect(reverse('ingester:publication-detail', args=(object_id,)))