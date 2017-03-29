
from ingester.Iingester import Iingester
from ingester.exception import IIngester_Exception
from django.test import TestCase, mock


class H1 (Iingester):
    def __init__(self,name):
        Iingester.__init__(self, name)
        self.query= "SELECT * FROM test"

    def get_global_url(self):
        pass

    def mapping_function(self, query_dataset):
        pass
    def update_harvested(self):
        pass


class TestIHarvest(TestCase):
    def test_init(self):
        x= H1("Hello")
        self.assertEqual(x.query,"SELECT * FROM test")
        self.assertEqual(x.limit,None)
        self.assertEqual(x.name, "Hello")

    def test_limit_none(self):
        x= H1("Hello")
        x.set_limit(None)
        self.assertEqual(x.limit,None)

    def test_limit_invalid(self):
        x= H1("Hello")
        self.assertRaises(IIngester_Exception,x.set_limit,"Hello")

    def test_limit_invalid_value(self):
        x= H1("Hello")
        self.assertRaises(IIngester_Exception,x.set_limit,-5)

    def test_limit_valid(self):
        x= H1("Hello")
        x.set_limit(5)
        self.assertEqual(x.limit,5)

    def test_query(self):
        x= H1("Hello")
        self.assertEqual(x.get_query(), "SELECT * FROM test")

    def test_query_limit(self):
        x= H1("Hello")
        x.set_limit(6)
        self.assertEqual(x.get_query(), "SELECT * FROM test LIMIT 6")








