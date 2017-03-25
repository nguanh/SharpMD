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


class TestCreatePublication(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)

    def test_no_publication(self):
        insert_data("INSERT INTO cluster (id,cluster_name) VALUES(1,'random Title')")
        insert_data("INSERT into authors (id,main_name,block_name)"
                    "VALUES(1,'Nina Nonsense','nonsense,n'),(2,'Otto Otter','otter,o')")
        insert_data("INSERT into pub_source (id,main_name,block_name,journal) "
                    "VALUES(1,'myJournal','myjournal','myJournal'),(2,'myJournal','myjournal','myJournal')")
        test_success = {
            "local_url": {
                (1,1,3,None,1, "TODO PLATZHALTER",datetime(1990,1,1,1,1,1)),
            },
            "publication":{
                (1,1,1,None,None,None,None,None,None,None,None,None,None,None)
            },
            "publication_authors" :{
                (1,1,1,0),
                (2,1,2,1)

            }
        }
        result = create_publication(self.connector,1,[1,2],3,1)
        self.assertEqual(result[0],1)
        compare_tables(self,test_success,ignore_id=True)

    def test_existing_publication(self):
        insert_data("INSERT INTO cluster (id,cluster_name) VALUES(1,'random Title')")
        insert_data("INSERT into authors (id,main_name,block_name)"
                    "VALUES(1,'Nina Nonsense','nonsense,n'),(2,'Otto Otter','otter,o')")

        insert_data("INSERT INTO global_url(id,domain,url) VALUES(5,'x','x')")
        insert_data("INSERT INTO local_url(id,global_url_id,url) VALUES(5,5,'bla')")

        insert_data("INSERT INTO publication(id,url_id,cluster_id) VALUES (5,5,1)")
        insert_data("INSERT into pub_source (id,main_name,block_name,journal) "
                    "VALUES(1,'myJournal','myjournal','myJournal'),(2,'myJournal','myjournal','myJournal')")
        result = create_publication( self.connector,1, [1, 2],1,2)
        test_success = {
            "publication_authors": {
                (1, 5, 1, 0),
                (2, 5, 2, 1)

            }
        }
        self.assertEqual(result[0], 5)
        compare_tables(self, test_success, ignore_id=True)

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)


class TestCreateTitle(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)

    def test_single_match(self):
        insert_data("INSERT INTO cluster (id,cluster_name) VALUES(1,'matching title')")
        title = "matching title"
        matching = {
            "status": Status.SAFE,
            "match": Match.SINGLE_MATCH,
            "id": 1,
            "reason": None,
        }

        result = create_title(matching,title, self.connector)
        self.assertEqual(result,1)

    def test_no_match(self):
        title = "matching title"
        matching = {
            "status": Status.SAFE,
            "match": Match.NO_MATCH,
            "id": None,
            "reason": None,
        }

        test_success = {
            "cluster": {
                (1, "matching title"),
            },
        }
        result = create_title(matching,title, self.connector)
        self.assertEqual(result, 1)
        compare_tables(self,test_success, ignore_id=True)

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)


class TestCreateAuthors(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)

    def test_success(self):
        insert_data("INSERT into global_url (id,domain,url) VALUES(5,'a','a')")
        insert_data("INSERT into local_url (id,url,global_url_id) VALUES(1,'a',5)")
        insert_data("INSERT into authors (id,main_name,block_name)"
                    "VALUES(1,'Nina Nonsense','nonsense,n'),(2,'Otto Otter','otter,o'),(3,'Orna Otter','otter,o')")
        insert_data("INSERT into name_alias(id,authors_id,alias)"
                    "VALUES(1,1,'Nina Nonsense'),(2,2,'Otto Otter'),(3,3,'Orna Otter')")
        authors_list=[{
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
        matching_list=[
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

        #resulting databasecontent
        test_success = {
            "authors": {
                (1, "Nina Nonsense", "nonsense,n", None, None, None, datetime(1990, 1, 1, 1, 1, 1), None),
                (2, "Otto Otter", "otter,o", None, None, None, datetime(1990, 1, 1, 1, 1, 1), None),
                (3, "Orna Otter", "otter,o", None, None, None, datetime(1990, 1, 1, 1, 1, 1), None),
                (4, "Melvin Master", "master,m", None, None, None, datetime(1990, 1, 1, 1, 1, 1), None),
            },
            "name_alias": {
                (1, 1, "Nina Nonsense"),
                (2, 2, "Otto Otter"),
                (3, 3, "Orna Otter"),
                (4, 4, "Melvin Master"),
            },
            "alias_source": {
                (3, 1, 1),
                (5, 1, 2),
                (1, 1, 4),
            },
            "publication_authors": {
                (1, 1, 4, 0),
                (2, 1, 1, 1),
                (3, 1, 2, 2),
            }

        }
        result = create_authors(matching_list, authors_list,1, self.connector)
        self.assertEqual(result,[4,1,2])
        compare_tables(self, test_success, ignore_id=True)

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)
