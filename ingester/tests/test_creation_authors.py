from django.test import TransactionTestCase
from ingester.helper import *
from ingester.creation_functions import create_authors
from ingester.models import *


class TestCreateAuthors(TransactionTestCase):

    def test_success(self):
        gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        lurl = local_url.objects.create(id=1, url="a", global_url=gurl)
        author1 = authors_model.objects.create(id=1, main_name="Nina Nonsense", block_name="nina nonsense")
        author2 = authors_model.objects.create(id=2, main_name="Ahmed Abdelli", block_name="ahmed abdelli")
        author3 = authors_model.objects.create(id=3, main_name="Ahmed Abdelli", block_name="ahmed abdelli")

        author_aliases.objects.bulk_create([
            author_aliases(id=1, alias="Nina Nonsense", author=authors_model.objects.get(id=1)),
            author_aliases(id=2, alias="Ahmed Abdelli", author=authors_model.objects.get(id=2)),
            author_aliases(id=3, alias="Ahmed Abdelli", author=authors_model.objects.get(id=3))
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
                "original_name": "Ahmed Abdelli",
                "parsed_name": "Ahmed Abdelli",
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
                "id": author1,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.MULTI_MATCH,
                "id": author2,
                "reason": None,
            }
        ]

        result = create_authors(matching_list, authors_list, lurl)
        print(result)
        self.assertEqual(result[0].id, 4)
        self.assertEqual(result[1].id, 1)
        self.assertEqual(result[2].id, 2)

        self.assertEqual(authors_model.objects.count(),4)
        self.assertEqual(author_aliases.objects.count(), 4)
        self.assertEqual(author_alias_source.objects.count(),3)
        self.assertEqual(authors_model.objects.get(id=4).main_name, "Melvin Master")
        self.assertEqual(authors_model.objects.get(id=4).block_name, "melvin master")

        self.assertEqual(publication_author.objects.get(priority=0).author.main_name, "Melvin Master")
        self.assertEqual(publication_author.objects.get(priority=1).author.main_name, "Nina Nonsense")
        self.assertEqual(publication_author.objects.get(priority=2).author.main_name, "Ahmed Abdelli")

    def test_regression(self):
        gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        lurl = local_url.objects.create(id=1, url="a", global_url=gurl)
        author1 = authors_model.objects.create(id=1, main_name="Nina Nonsense", block_name="nina nonsense")
        author2 = authors_model.objects.create(id=2, main_name="Ahmed Abdelli", block_name="ahmed abdelli")

        author_aliases.objects.bulk_create([
            author_aliases(id=1, alias="Nina Nonsense", author=authors_model.objects.get(id=1)),
            author_aliases(id=2, alias="Ahmed Abdelli", author=authors_model.objects.get(id=2)),
        ]
        )

        authors_list = [
            {
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
                "original_name": "Ahmed Abdelli",
                "parsed_name": "Ahmed Abdelli",
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
                "id": author1,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author2,
                "reason": None,
            }
        ]

        result = create_authors(matching_list, authors_list, lurl)
        self.assertEqual(authors_model.objects.count(),3)
        self.assertEqual(result[0].id, 3)
        self.assertEqual(result[1].id, 1)
        self.assertEqual(result[2].id, 2)
        # self.assertEqual(author_aliases.objects.count(),4)
        for obj in author_aliases.objects.all():
            print(obj.test())
        # check database
        for obj in author_alias_source.objects.all():
            print(obj.test())
        self.assertEqual(author_alias_source.objects.count(), 3)

        self.assertEqual(author_aliases.objects.count(), 3)
        self.assertEqual(authors_model.objects.get(id=3).main_name, "Melvin Master")
        self.assertEqual(authors_model.objects.get(id=3).block_name, "melvin master")

        self.assertEqual(publication_author.objects.get(priority=0).author.main_name, "Melvin Master")
        self.assertEqual(publication_author.objects.get(priority=1).author.main_name, "Nina Nonsense")
        self.assertEqual(publication_author.objects.get(priority=2).author.main_name, "Ahmed Abdelli")

    def test_regression_2(self):
        # testing possible duplicate publication authors
        gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        lurl = local_url.objects.create(id=1, url="a", global_url=gurl)
        author1 = authors_model.objects.create(id=1, main_name="Nina Nonsense", block_name="nina nonsense")
        author2 = authors_model.objects.create(id=2, main_name="Ahmed Abdelli", block_name="ahmed abdelli")
       # publication_author.objects.create(url=lurl, author=author1, priority=0)
       # publication_author.objects.create(url=lurl, author=author1, priority=2)
        author_aliases.objects.bulk_create([
            author_aliases(id=1, alias="Nina Nonsense", author=authors_model.objects.get(id=1)),
            author_aliases(id=2, alias="Ahmed Abdelli", author=authors_model.objects.get(id=2)),
        ]
        )

        authors_list = [
            {
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
                "original_name": "Ahmed Abdelli",
                "parsed_name": "Ahmed Abdelli",
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
                "id": author1,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author2,
                "reason": None,
            }
        ]

        result = create_authors(matching_list, authors_list, lurl)
        self.assertEqual(authors_model.objects.count(),3)
        self.assertEqual(result[0].id, 3)
        self.assertEqual(result[1].id, 1)
        self.assertEqual(result[2].id, 2)

        for obj in publication_author.objects.all():
            print(obj.test())

        self.assertEqual(author_alias_source.objects.count(), 3)

        self.assertEqual(author_aliases.objects.count(), 3)
        self.assertEqual(authors_model.objects.get(id=3).main_name, "Melvin Master")
        self.assertEqual(authors_model.objects.get(id=3).block_name, "melvin master")

        self.assertEqual(publication_author.objects.get(priority=0).author.main_name, "Melvin Master")
        self.assertEqual(publication_author.objects.get(priority=1).author.main_name, "Nina Nonsense")
        self.assertEqual(publication_author.objects.get(priority=2).author.main_name, "Ahmed Abdelli")