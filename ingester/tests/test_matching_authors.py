from django.test import TestCase,TransactionTestCase

from ingester.helper import *
from ingester.matching_functions import match_author
from ingester.models import authors_model, author_aliases, author_alias_source



class TestMatchAuthors(TransactionTestCase):

    def test_success_empty_db(self):
        authors=[{
            "original_name": "Karl Bauer",
            "parsed_name": "Karl Bauer",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        {
            "original_name": "Jarl Mauer",
            "parsed_name": "Jarl Mauer",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)
        self.assertEqual(result,[{
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            }
        ])


    def test_single_block_match(self):
        authors_model.objects.create(id=5, main_name ="Hans Gruber")
        authors = [{
            "original_name": "Hans Meyer Gruber",
            "parsed_name": "Hans Meyer Gruber",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)

        self.assertEqual(result,[{
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": 5,
                "reason": None,
            },
        ])

    def test_multi_block_alias_match(self):
        author1 = authors_model.objects.create(id=5, main_name="Hans Gruber")
        author2 = authors_model.objects.create(id=1, main_name="Heinrich Gruber")

        author_aliases.objects.bulk_create([
            author_aliases(id=1, author=author2, alias="Heinrich Gruber"),
            author_aliases(id=2, author=author2, alias="Heinrich F. Gruber"),
            author_aliases(id=3, author=author1, alias="Hans Gruber"),
            author_aliases(id=4, author=author1, alias="Hans Meyer Gruber"),
        ])

        authors = [{
            "original_name": "Hans Meyer Gruber",
            "parsed_name": "Hans Meyer Gruber",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)

        self.assertEqual(result,[{
                "status": Status.SAFE,
                "match": Match.MULTI_MATCH,
                "id": 5,
                "reason": None,
            },
        ])

    def test_multi_block_alias_no_match(self):
        author1 = authors_model.objects.create(id=5, main_name="Hans Gruber")
        author2 = authors_model.objects.create(id=1, main_name="Heinrich Gruber")

        author_aliases.objects.bulk_create([
            author_aliases(id=1, author=author2, alias="Heinrich Gruber"),
            author_aliases(id=2, author=author2, alias="Heinrich F. Gruber"),
            author_aliases(id=3, author=author1, alias="Heinrich Gruber"),
            author_aliases(id=4, author=author1, alias="Heinrich F. Gruber"),
        ])
        authors = [{
            "original_name": "Hans Meyer Gruber",
            "parsed_name": "Hans Meyer Gruber",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)

        self.assertEqual(result, [{
            "status": Status.LIMBO,
            "match": Match.MULTI_MATCH,
            "id": None,
            "reason": Reason.AMB_ALIAS,
        },
        ])

    def test_regression(self):
        author1 = authors_model.objects.create(id=21, main_name="Yi Wang")
        author2 = authors_model.objects.create(id=22, main_name="Yang Wang")
        alias1 = author_aliases.objects.create(id=23, alias="Yi Wang", author=author1)
        alias2 = author_aliases.objects.create(id=24, alias="Yang Wang", author = author2)
        authors = [{
            "original_name": "Yiding Wang",
            "parsed_name": "Yiding Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)
        print(result)

    def test_regression_2(self):
        author1 = authors_model.objects.create(id=21, main_name="Yi Wang")
        alias1 = author_aliases.objects.create(id=23, alias="Yi Wang", author=author1)

        authors = [{
            "original_name": "Yang Wang",
            "parsed_name": "Yang Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]

        authors2 = [{
            "original_name": "Yiyang Wang",
            "parsed_name": "Yiyang Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        authors3 = [{
            "original_name": "Yennifer Wang",
            "parsed_name": "Yennifer Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = match_author(authors)
        result2 = match_author(authors2)
        result3 = match_author(authors3)
        print(result)
        print(result2)
        print(result3)


