from unittest import TestCase

from ingester.helper import *
from ingester.ingester import match_author, match_title, match_type, match_pub_source
from ingester.setup_database import setup_database
from mysqlWrapper.mariadb import MariaDb
from .ingester_tools import TESTDB, delete_database, insert_data, get_pub_source, compare_tables


class TestMatchPubSource(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)
        insert_data("INSERT into global_url (id,domain,url) VALUES(5,'a','a')")
        insert_data("INSERT into local_url (id,url,global_url_id) VALUES(1,'a',5)")

    def test_none(self):
        data = get_pub_source()
        identifier = match_pub_source(data,1, self.connector)
        self.assertEqual(identifier, None)

    def test_no_match(self):
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_source(data,1, self.connector)
        test_success = {
            "pub_source": {
                (1,"myJournal","myjournal",None,None,None,None,None,None,None,None,None,None,"myJournal"),
            },
            "pub_source_alias": {
                (1,1,"myJournal")
            },
            "pub_source_source": {
                (1,1,1),
            }
        }
        self.assertEqual(identifier, 1)
        compare_tables(self,test_success)

    def test_single_match(self):
        insert_data("INSERT into pub_source (id,main_name,block_name,journal) "
                    "VALUES(1,'myJournal','myjournal','myJournal')")
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_source(data,1, self.connector)

        test_success = {
            "pub_source": {
                (1,"myJournal","myjournal",None,None,None,None,None,None,None,None,None,None,"myJournal"),
            },
            "pub_source_alias": {
                (1,1,"myJournal")
            },
            "pub_source_source": {
                (1,1,1),
            }
        }
        self.assertEqual(identifier, 1)
        compare_tables(self, test_success)

    def test_multi_match_single_alias(self):
        insert_data("INSERT into pub_source (id,main_name,block_name,journal) "
                    "VALUES(1,'myJournal','myjournal','myJournal'),(2,'myJournal','myjournal','myJournal')")
        insert_data("INSERT into pub_source_alias (id,pub_source_id,alias) "
                    "VALUES(1,1,'MyJournal?'), (2,2,'myJournal')"
                    )
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_source(data, 1, self.connector)

        test_success = {
            "pub_source_alias": {
                (1, 1, "MyJournal?"),
                (2, 2, "myJournal"),
            },
            "pub_source_source": {
                (1, 1, 2),
            }
        }
        self.assertEqual(identifier, 2)
        compare_tables(self,test_success)

    def test_multi_match_multi_alias(self):
        insert_data("INSERT into pub_source (id,main_name,block_name,journal) "
                    "VALUES(1,'myJournal','myjournal','myJournal'),(2,'myJournal','myjournal','myJournal')")
        insert_data("INSERT into pub_source_alias (id,pub_source_id,alias) "
                    "VALUES(1,1,'myJournal'), (2,2,'myJournal')"
                    )
        data = get_pub_source(key="myJournal", journal="myJournal")
        identifier = match_pub_source(data, 1, self.connector)

        test_success = {
            "pub_source_alias": {
                (1, 1, "myJournal"),
                (2, 2, "myJournal"),
                (3, 3, "myJournal"),
            },
            "pub_source_source": {
                (1, 1, 3),
            }
        }
        self.assertEqual(identifier, 3)
        compare_tables(self,test_success)


    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)


class TestMatchType(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)


    def test_success(self):
        identifier = match_type('article', self.connector)
        self.assertEqual(identifier, 1)

    def test_no_matching_type(self):
        identifier = match_type('blubb', self.connector)
        self.assertEqual(identifier, 2)

    def test_no_matching_type2(self):
        identifier = match_type(None, self.connector)
        self.assertEqual(identifier, 2)

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)


class TestMatchTitle(TestCase):
    def setUp(self):
        setup_database(TESTDB)
        self.connector = MariaDb(db=TESTDB)

    def test_success_empty_db(self):

        result = match_title("Single Title", self.connector)
        self.assertEqual(result,{
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            })

    def test_multi_cluster_match(self):
        insert_data("INSERT into cluster (id,cluster_name) VALUES(1,'multi title'),(2,'multi title')")
        result = match_title("Multi Title", self.connector)
        self.assertEqual(result,{
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_CLUSTER,
            })

    def test_single_cluster_single_pub(self):
        insert_data("INSERT into global_url (id,domain,url) VALUES(5,'a','a')")
        insert_data("INSERT into local_url (id,url,global_url_id) VALUES(1,'a',5)")
        insert_data("INSERT into cluster (id,cluster_name) VALUES(1,'multi title'),(2,'single title')")
        insert_data("INSERT into publication(id,url_id,cluster_id, title)VALUES (1,1,2,'hi')")
        result = match_title("single Title", self.connector)
        self.assertEqual(result,{
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": 2,
                "reason": None,
            })

    def test_single_cluster_multi_no_pub(self):
        insert_data("INSERT into global_url (id,domain,url) VALUES(5,'a','a')")
        insert_data("INSERT into local_url (id,url,global_url_id) VALUES(1,'a',5)")
        insert_data("INSERT into cluster (id,cluster_name) VALUES(1,'multi title'),(2,'single title')")
        # no publications for cluster, why so ever
        result = match_title("single Title", self.connector)
        self.assertEqual(result,{
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_PUB,
            })

    def tearDown(self):
        self.connector.close_connection()
        delete_database(TESTDB)
        pass

