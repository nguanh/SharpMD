from unittest import TestCase
from dblp.helper import parse_mdate, parse_year
from datetime import datetime
from dblp.exception import IHarvest_Exception

class TestParse_mdate(TestCase):
    def test_parse_mdate_success(self):
        self.assertEqual(parse_mdate("1995-4-12"),datetime(1995,4,12))

    def test_parse_mdate_fail(self):
        self.assertRaises(IHarvest_Exception, parse_mdate, "hallo")


class TestParse_year(TestCase):
    def test_success(self):
        self.assertEqual(parse_year("1991"), datetime(1991,1,1))

    def test_fail_value(self):
        self.assertRaises(IHarvest_Exception, parse_year, "fd")

class TestDict_to_tuple(TestCase):
    pass