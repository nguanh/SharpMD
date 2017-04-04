from datetime import datetime
from unittest import TestCase

from ingester.difference_storage import *
from ingester.helper import *
from ingester.ingester import create_authors, create_title, create_publication, update_diff_tree
from ingester.setup_database import setup_database
from mysqlWrapper.mariadb import MariaDb
from .ingester_tools import TESTDB, delete_database, insert_data, compare_tables, get_pub_dict


class TestUpdateDiffTree(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)

    def test_no_diff_tree(self):
        insert_data("INSERT INTO publication(id,url_id,cluster_id) VALUES (5,5,1)")
        # every table is empty
        pub_dict = get_pub_dict(url_id=1, title="Hello World", date_published=datetime(1990,1,1,1,1,1))
        author_ids=[1,4,7]
        result = update_diff_tree(5,pub_dict,author_ids,self.connector)
        self.assertEqual(result["author_ids"],[
            {"value": 1, "votes": 0, "bitvector": 1},
            {"value": 4, "votes": 0, "bitvector": 1},
            {"value": 7, "votes": 0, "bitvector": 1}
        ])

    def test_existing_diff_tree(self):
        pub_dict = get_pub_dict(url_id=1, title="Hello World Again", date_published=datetime(1990, 1, 1, 1, 1, 1), author_ids=5)
        diff_tree = generate_diff_store(pub_dict)
        serialized_tree = serialize_diff_store(diff_tree)
        insert_data("INSERT INTO publication(id,url_id,cluster_id, differences) "
                    "VALUES (5,5,1,%s)",(serialized_tree,))
        author_ids=[1,4,7]
        pub_dict = get_pub_dict(url_id=2, title="Hello World", date_published=datetime(1990, 1, 1, 1, 1, 1))
        result = update_diff_tree(5,pub_dict,author_ids,self.connector)

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
        insert_data("INSERT INTO publication(id,url_id,cluster_id, differences) "
                    "VALUES (5,5,1,%s)",(serialized_tree,))
        author_ids=[1,4,7]
        pub_dict = get_pub_dict(url_id=2, title="Hello World", date_published=datetime(1990, 1, 1, 1, 1, 1))
        result = update_diff_tree(5,pub_dict,author_ids,self.connector)

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

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)

