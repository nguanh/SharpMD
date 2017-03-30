from django.test import TestCase
from ingester.helper import *
from ingester.creation_functions import create_authors
from ingester.models import *


class TestCreateAuthors(TestCase):

    def test_success(self):
        gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        lurl = local_url.objects.create(id=1, url="a", global_url=gurl)
        authors_model.objects.bulk_create([
            authors_model(id=1, main_name="Nina Nonsense", block_name="nonsense,n"),
            authors_model(id=2, main_name="Otto Otter", block_name="otter,o"),
            authors_model(id=3, main_name="Orna Otter", block_name="otter,o"),
        ])
        author_aliases.objects.bulk_create([
            author_aliases(id=1, alias="Nina Nonsense", author=authors_model.objects.get(id=1)),
            author_aliases(id=2, alias="Otto Otter", author=authors_model.objects.get(id=2)),
            author_aliases(id=3, alias="Orna Otter", author=authors_model.objects.get(id=3))
            ]
        )

        authors_list = [{
            "original_name": "Melvin Master",
            "parsed_name": "Melvin Master",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
            },
            {
                "original_name": "Nina Nonsense",
                "parsed_name": "Nina Nonsense",
                "website": None,
                "contact": None,
                "about": None,
                "modified": None,
                "orcid_id": None,
            },
            {
                "original_name": "Otto Otter",
                "parsed_name": "Otto Otter",
                "website": None,
                "contact": None,
                "about": None,
                "modified": None,
                "orcid_id": None,
            }
        ]
        matching_list = [
            {
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": 1,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.MULTI_MATCH,
                "id": 2,
                "reason": None,
            }
        ]

        result = create_authors(matching_list, authors_list, lurl)
        self.assertEqual(result[0].id, 4)
        self.assertEqual(result[1].id, 1)
        self.assertEqual(result[2].id, 2)
        # check database
        self.assertEqual(author_alias_source.objects.count(), 3)

        self.assertEqual(author_aliases.objects.count(), 4)
        self.assertEqual(authors_model.objects.get(id=4).main_name, "Melvin Master")
        self.assertEqual(authors_model.objects.get(id=4).block_name, "master,m")

        self.assertEqual(publication_author.objects.get(priority=0).author.main_name, "Melvin Master")
        self.assertEqual(publication_author.objects.get(priority=1).author.main_name, "Nina Nonsense")
        self.assertEqual(publication_author.objects.get(priority=2).author.main_name, "Otto Otter")

