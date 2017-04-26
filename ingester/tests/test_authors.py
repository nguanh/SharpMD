from django.test import TransactionTestCase
from ingester.matching_functions import match_author
from ingester.creation_functions import create_authors
from ingester.models import *



class TestAuthors(TransactionTestCase):

    def setUp(self):
        self.gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        self.lurl = local_url.objects.create(id=1, url="a", global_url=self.gurl)
        self.authors = [{
            "original_name": "Karl Bauer",
            "parsed_name": "Karl Bauer",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
            {
                "original_name": "Hans",
                "parsed_name": "Meyer",
                "website": None,
                "contact": None,
                "about": None,
                "modified": None,
                "orcid_id": None,
            },
        ]


    def test_long(self):
        for i in range(1000):
            lurl = local_url.objects.create(url="a", global_url=self.gurl)
            matches = match_author(self.authors)
            id_list = create_authors(matches, self.authors, lurl)

        for x in authors_model.objects.all():
            print(x.test())
        self.assertEqual(authors_model.objects.count(),2)