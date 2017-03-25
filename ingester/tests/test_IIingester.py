from unittest import TestCase

from ingester.Iingester import Iingester
from ingester.exception import IIngester_Exception


class Dummy (Iingester):
    def __init__(self):
        Iingester.__init__(self)
        self.query = "SELECT * FROM test"

    def get_global_url(self):
        pass

    def mapping_function(self, query_dataset):
        pass
    def update_harvested(self):
        pass

    def get_name(self):
        pass


class TestIIngester(TestCase):

    def test_set_limit_invalid1(self):
        tmp = Dummy()
        self.assertRaises(IIngester_Exception,tmp.set_limit,"Hallo")

    def test_set_limit_invalid1(self):
        tmp = Dummy()
        self.assertRaises(IIngester_Exception,tmp.set_limit,0)

    def test_get_query_no_limit(self):
        tmp = Dummy()
        result = tmp.get_query()
        self.assertEqual(result, "SELECT * FROM test")

    def test_get_query_limit(self):
        tmp = Dummy()
        tmp.set_limit(100)
        result = tmp.get_query()
        self.assertEqual(result, "SELECT * FROM test LIMIT 100")



