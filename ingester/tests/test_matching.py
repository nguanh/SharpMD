from unittest import TestCase

from ingester.helper import *
from ingester.ingester import match_author, match_title, match_type, match_pub_source
from ingester.setup_database import setup_database
from mysqlWrapper.mariadb import MariaDb
from .ingester_tools import TESTDB, delete_database, insert_data, get_pub_source, compare_tables



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

