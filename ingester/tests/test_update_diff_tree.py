from django.test import TestCase,mock
from ingester.models import *
from ingester.difference_storage import *
from ingester.creation_functions import update_diff_tree
from datetime import datetime

from .ingester_tools import get_pub_dict


class TestUpdateDiffTree(TestCase):
    def setUp(self):
        self.gurl = global_url.objects.create(id=1, domain="http://dummy.de", url="http://dummy.de")
        self.lurl = local_url.objects.create(id=1, url="a", global_url=self.gurl)
        self.cluster_id = cluster.objects.create(id=1, name="random Title")

    def test_no_diff_tree(self):
        pub = publication.objects.create(id=5, url=self.lurl, cluster=self.cluster_id, title="test title")
        # every table is empty
        pub_dict = get_pub_dict(url_id=1, title="Hello World", date_published=datetime(1990,1,1,1,1,1))
        author_ids=[1,4,7]
        result = update_diff_tree(pub, pub_dict,author_ids)
        self.assertEqual(result["author_ids"],[
            {"value": 1, "votes": 0, "bitvector": 1},
            {"value": 4, "votes": 0, "bitvector": 1},
            {"value": 7, "votes": 0, "bitvector": 1}
        ])

    def test_existing_diff_tree(self):
        pub_dict = get_pub_dict(url_id=1, title="Hello World Again", date_published=datetime(1990, 1, 1, 1, 1, 1),
                                author_ids=5)
        diff_tree = generate_diff_store(pub_dict)
        serialized_tree = serialize_diff_store(diff_tree)
        print(serialized_tree)
        pub = publication.objects.create(id=5, url=self.lurl, cluster=self.cluster_id, title="test title",
                                         differences=serialized_tree)
        author_ids=[1,4,7]
        pub_dict = get_pub_dict(url_id=2, title="Hello World", date_published=datetime(1990, 1, 1, 1, 1, 1))
        result = update_diff_tree(pub,pub_dict,author_ids)

        self.assertEqual(result["author_ids"],[
            {"value": 5, "votes": 0, "bitvector": 1},
            {"value": 1, "votes": 0, "bitvector": 2},
            {"value": 4, "votes": 0, "bitvector": 2},
            {"value": 7, "votes": 0, "bitvector": 2}
        ])

    def test_full_dataset(self):

        pub_dict = get_pub_dict(url_id=1, title="Hello World Again",
                                date_published=datetime(1990, 1, 1, 1, 1, 1),
                                type_ids=5,
                                keyword_ids=1,
                                study_field_ids=1,
                                pub_source_ids=1,
                                volume="5",
                                number="5",
                                pages="1-3",
                                note="note",
                                doi="doi",
                                abstract="abstract",
                                copyright="copyright",
                                date_added=datetime(1990, 1, 1, 1, 1, 1),
                                author_ids=5)
        diff_tree = generate_diff_store(pub_dict)
        serialized_tree = serialize_diff_store(diff_tree)
        pub = publication.objects.create(id=5, url=self.lurl, cluster=self.cluster_id, title="test title",
                                         differences=serialized_tree)
        author_ids=[1,4,7]
        pub_dict = get_pub_dict(url_id=2, title="Hello World", date_published=datetime(1990, 1, 1, 1, 1, 1))
        result = update_diff_tree(pub,pub_dict,author_ids)

        self.assertEqual(result["type_ids"][0]["value"],5)
        self.assertEqual(result["pub_source_ids"][0]["value"], 1)
        self.assertEqual(result["keyword_ids"][0]["value"], 1)
        self.assertEqual(result["study_field_ids"][0]["value"], 1)
        self.assertEqual(result["abstract"][0]["value"], "abstract")
        self.assertEqual(result["copyright"][0]["value"], "copyright")
        self.assertEqual(result["note"][0]["value"], "note")
        self.assertEqual(result["doi"][0]["value"], "doi")
        self.assertEqual(result["date_added"][0]["value"], "1990-01-01 01:01:01")
        self.assertEqual(result["pages"][0]["value"], "1-3")
        self.assertEqual(result["number"][0]["value"], "5")
        self.assertEqual(result["volume"][0]["value"], "5")


