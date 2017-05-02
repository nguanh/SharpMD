from .models import *
from django.db import transaction

from ingester.matching_functions import search_title


class Referencer:

    def __init__(self, limit, chunk_size=5):
        self.limit = limit
        self.chunk_size = chunk_size

    def run(self):
        count = 0
        while count < self.limit:
            reference_list = []
            delete_list = []
            #TODO include INCOMPLETE
            single_ref_list = SingleReference.objects.filter(status="OP").all().values('title','status')[:self.chunk_size]
            for single_ref in single_ref_list:
                title_matches = search_title(single_ref.title)
                if len(title_matches) == 1:
                    status = 'FIN'
                    reference_list.append(PubReference(cluster=title_matches[0]))
                    delete_list.append(single_ref)
                else:
                    if len(title_matches) == 0:
                        status = 'INC'
                    else:
                        status = 'LIM'
            count += len(single_ref_list)
            PubReference.objects.bulk_create(reference_list)



