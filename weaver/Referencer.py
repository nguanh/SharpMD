from .models import SingleReference,OpenReferences
from ingester.models import PubReference
from ingester.helper import normalize_title
from django.db import transaction
from django.db.models import Q
from datetime import date
import logging
from django.db.utils import IntegrityError
from ingester.matching_functions import search_title
import datetime

LIMBO_LIMIT = 5


class Referencer:
    def __init__(self, limit, logger=None):
        self.limit = limit
        if logger is None:
            self.logger = logging.getLogger()
        else:
            self.logger = logger

    def run(self,test_mode=False):
        today = date.today()
        compare_date = date.today() if test_mode is False else date.today() + datetime.timedelta(days=1)
        reference_list = []
        # fetch all single_references of an open_ref
        # fetch open_references to gather all ingester url_objects
        openreference_list = OpenReferences.objects.filter(last_updated__lt=compare_date).select_related('ingester_key').only('ingester_key')[:self.limit]
        for open_ref in openreference_list:
            open_ref.last_updated = today
            open_ref.save()
            single_ref_list = SingleReference.objects.filter(source=open_ref).filter(Q(status='OP')| Q(status='INC')).only('tries', 'title', 'status').all()

            for single_ref in single_ref_list:
                title_matches = search_title(single_ref.title, threshold=0.8)
                if len(title_matches) == 1:
                    # single match: create reference for only match
                    PubReference.objects.get_or_create(reference =title_matches[0], source=open_ref.ingester_key,
                                                       defaults={'original_title': single_ref.title,
                                                                 'original_key': single_ref.id})
                    #reference_list.append(PubReference(reference=title_matches[0], source=open_ref.ingester_key, original_title=single_ref.title))
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
                            PubReference.objects.get_or_create(reference=title, source=open_ref.ingester_key,
                                                               defaults={'original_title': single_ref.title,
                                                                         'original_key': single_ref.id})
                            #reference_list.append(PubReference(reference=title, source=open_ref.ingester_key, original_title=single_ref.title))
                single_ref.save()
        try:
            PubReference.objects.bulk_create(reference_list)
        except IntegrityError:
            # duplicate key on insert, insert everything manually
            for element in reference_list:
                print("Rollback")
                PubReference.objects.get_or_create(reference =element.reference,
                                                   source=element.source,
                                                   original_title=single_ref.title,
                                                   original_key=single_ref.id)



        #SingleReference.objects.filter(status='FIN').delete()



