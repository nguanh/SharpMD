from django.test import TransactionTestCase
from mysqlWrapper.mariadb import MariaDb
from ingester.helper import *
from ingester.matching_functions import advanced_author_match
from ingester.models import authors_model, author_aliases, author_alias_source


class TestMatchAuthors(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex(("CREATE FULLTEXT INDEX authors_model_ft_idx ON test_storage.ingester_authors_model (block_name)"), ())
        connector.close_connection()

    @classmethod
    def tearDownClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex("ALTER TABLE test_storage.ingester_authors_model DROP INDEX authors_model_ft_idx", ())
        connector.close_connection()

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
        result = advanced_author_match(authors)
        self.assertEqual(result, [{
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

    def test_single_alias_match(self):
        author = authors_model.objects.create(id=5, main_name ="Hans Gruber")
        authors = [{
            "original_name": "Hans. Gruber",
            "parsed_name": "Hans. Gruber",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        ]
        result = advanced_author_match(authors)

        self.assertEqual(result, [{
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author,
                "reason": None,
            },
        ])

    def test_single_match_strat_2(self):
        author1 = authors_model.objects.create(main_name="Han Lin Xuu")
        author2 = authors_model.objects.create(main_name="Han Xiu Lin")

        author_aliases.objects.create(author=author1, alias="Han Lin Xuu")
        author_aliases.objects.create(author=author1, alias="Han Xuu Lin")
        author_aliases.objects.create(author=author2, alias="Han Lin Xiu")
        author_aliases.objects.create(author=author2, alias="Han Lin")

        authors = [{
            "original_name": "Han Xiu",
            "parsed_name": "Han Xiu",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        }]

        result = advanced_author_match(authors)
        self.assertEqual(result,[{
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author2,
                "reason": None,
            },
        ])

    def test_no_match_strat_2(self):
        author1 = authors_model.objects.create(main_name="Han Lin Xuu")
        author2 = authors_model.objects.create(main_name="Han Xiu Lin")

        author_aliases.objects.create(author=author1, alias="Han Lin Xuu")
        author_aliases.objects.create(author=author1, alias="Han Xuu Lin")
        author_aliases.objects.create(author=author2, alias="Han Lin Xiu")
        author_aliases.objects.create(author=author2, alias="Han Lin")

        authors = [{
            "original_name": "Han Solo",
            "parsed_name": "Han Solo",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        }]

        result = advanced_author_match(authors)
        self.assertEqual(result,[{
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            },
        ])

    def test_multi_match_strat_2(self):
        author1 = authors_model.objects.create(main_name="Han Lin Xuu")
        author2 = authors_model.objects.create(main_name="Han Xiu Lin")

        author_aliases.objects.create(author=author1, alias="Han Lin Xuu")
        author_aliases.objects.create(author=author1, alias="Han Xuu Lin")
        author_aliases.objects.create(author=author2, alias="Han Lin Xiu")

        authors = [{
            "original_name": "Han Lin",
            "parsed_name": "Han Lin",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        }]

        result = advanced_author_match(authors)
        self.assertEqual(result,[{
                    "status": Status.LIMBO,
                    "match": Match.MULTI_MATCH,
                    "id": None,
                    "reason": Reason.AMB_NAME_BLOCK
                }])

    """
    def test_regression(self):
        #TODO test schlägt fehl, weil suche noch nach allen namen gleichermaßen sucht
        author1 = authors_model.objects.create(id=21, main_name="Yi Wang")
        author2 = authors_model.objects.create(id=22, main_name="Yang Wang")
        alias1 = author_aliases.objects.create(id=23, alias="Yi Wang", author=author1)
        alias2 = author_aliases.objects.create(id=24, alias="Yang Wang", author = author2)
        authors = [{
            "original_name": "Yi ding Wang",
            "parsed_name": "Yi ding Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },
        {
            "original_name": "Yiding Wang",
            "parsed_name": "Yiding Wang",
            "website": None,
            "contact": None,
            "about": None,
            "modified": None,
            "orcid_id": None,
        },

        ]
        result = advanced_author_match(authors)
        print(result)
        self.assertEqual(result,[
            {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": author1,
                "reason": None,
            },
            {
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            },
        ])
    """