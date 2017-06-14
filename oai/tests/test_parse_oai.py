import logging
from unittest import TestCase

from harvester.exception import IHarvest_Exception
from oai.oaimph_parser import harvestOAI
from mysqlWrapper.tests.Mariadb_stub import Mariadb_test

class TestParseOai(TestCase):
    valid_link = 'http://citeseerx.ist.psu.edu/oai2'
    name = "OAI_HARVESTER"
    logger = logging.getLogger("TEST")


    def test_sql_fail(self):
        self.assertRaises(IHarvest_Exception, harvestOAI, self.valid_link,None,self.logger)

    def test_link_fail(self):
        test_db = Mariadb_test()
        self.assertRaises(IHarvest_Exception, harvestOAI,"hkjlkj",test_db,self.logger)

    def test_parameter_fail(self):
        test_db = Mariadb_test()
        self.assertRaises(IHarvest_Exception, harvestOAI,self.valid_link,test_db,self.logger,startDate="98790",endDate="gjhhk")

    def test_no_results(self):
        test_db = Mariadb_test()
        self.assertEqual(0, harvestOAI(self.valid_link,test_db,self.logger,startDate="1900-01-01",endDate="1900-01-01"))


    def test_valid(self):
        test_db = Mariadb_test()
        result = harvestOAI(self.valid_link, test_db,self.logger, startDate="2013-01-01", endDate="2013-01-01")
        self.assertEqual(result, 1)
        self.assertEqual((test_db.getList()[0]), 'http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.251.2812;')


