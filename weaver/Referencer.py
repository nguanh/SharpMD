from .models import *
from ingester.helper import normalize_title
from django.db import transaction
from django.db.models import Q
from datetime import date
import logging

from ingester.matching_functions import search_title

LIMBO_LIMIT = 5


class Referencer:
    def __init__(self, limit, logger=None):
        self.limit = limit
        if logger is None:
            self.logger = logging.getLogger()
        else:
            self.logger = logger

    def run(self):
        today = date.today()
        reference_list = []
        # fetch all single_references of an open_ref
        # fetch open_references to gather all ingester url_objects
        openreference_list = OpenReferences.objects.filter(last_updated__lt=date.today()).select_related('ingester_key').only('ingester_key')[:self.limit]

        for open_ref in openreference_list:
            open_ref.last_updated = today
            open_ref.save()
            single_ref_list = SingleReference.objects.filter(source=open_ref).filter(Q(status='OP')| Q(status='INC')).only('tries', 'title', 'status').all()

            for single_ref in single_ref_list:
                title_matches = search_title(single_ref.title, threshold=0.5)
                if len(title_matches) == 1:
                    # single match: create reference for only match
                    reference_list.append(PubReference(reference=title_matches[0], source=open_ref.ingester_key))
                    single_ref.status = 'FIN'
                elif len(title_matches) == 0:
                    # no match: increment tries and set as incomplete
                    single_ref.tries += 1
                    single_ref.status = 'INC' if single_ref.tries < LIMBO_LIMIT else 'LIM'
                else:
                    # multi match:
                    normal_title = normalize_title(single_ref.title)
                    single_ref.status = 'LIM'
                    for title in title_matches:
                        if title.name == normal_title:
                            single_ref.status = 'FIN'
                            reference_list.append(PubReference(reference=title, source=open_ref.ingester_key))
                single_ref.save()
        PubReference.objects.bulk_create(reference_list)
        SingleReference.objects.filter(status='FIN').delete()



