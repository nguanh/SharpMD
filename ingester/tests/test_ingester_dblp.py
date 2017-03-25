from unittest import TestCase

from dblp.queries import DBLP_ARTICLE, ADD_DBLP_ARTICLE
from dblp.dblpingester import DblpIngester
from ingester.ingester import ingest_data2
from ingester.setup_database import setup_database
from ingester.exception import IIngester_Exception
from .ingester_tools import compare_tables, delete_database,setup_tables,TESTDB,get_table_data,insert_data
import datetime


#TODO weitere tabellen hinzufügen
test_success = {
    "local_url": {
        (1, 3, 1, None, 1, 'journals/acta/AkyildizB89', datetime.datetime(1990, 1, 1, 1, 1, 1)),
        (2, 1, 1, None, 1, 'TODO PLATZHALTER', datetime.datetime(1990, 1, 1, 1, 1, 1)),
        (3, 3, 1, None, 1, 'journals/acta/VoglerS014', datetime.datetime(1990, 1, 1, 1, 1, 1)),
        (4, 1, 1, None, 1, 'TODO PLATZHALTER', datetime.datetime(1990, 1, 1, 1, 1, 1)),
    },
    "authors": {
        (1, "Ian F. Akyildiz", "akyildiz,i", None, None, None, datetime.datetime(1990, 1, 1, 1, 1, 1), None),
        (2, "Horst von Brand", "von brand,h", None, None, None, datetime.datetime(1990, 1, 1, 1, 1, 1), None),
        (3, "Walter Vogler", "vogler,w", None, None, None, datetime.datetime(1990, 1, 1, 1, 1, 1), None),
        (4, "Christian Stahl", "stahl,c", None, None, None, datetime.datetime(1990, 1, 1, 1, 1, 1), None),
        (5, "Richard Müller", "muller,r", None, None, None, datetime.datetime(1990, 1, 1, 1, 1, 1), None)
    },
    "name_alias": {
        (1, 1, "Ian F. Akyildiz"),
        (3, 2, "Horst von Brand"),
        (5, 3, "Walter Vogler"),
        (7, 4, "Christian Stahl"),
        (9, 5, "Richard Müller 0001"),
        (10, 5, "Richard Müller"),
    },
    "cluster": {
        (1, "bla bla bla"),
        (2, "kam kim kum")
    },

    "alias_source": {
        (1, 1, 1),
        (3, 1, 3),
        (5, 3, 5),
        (7, 3, 7),
        (9, 3, 9),
        (10, 3, 10),
    },

    "publication_authors": {
        (1, 1, 1, 0),
        (2, 1, 2, 1),
        (3, 2, 1, 0),
        (4, 2, 2, 1),
        (5, 3, 3, 0),
        (6, 3, 4, 1),
        (7, 3, 5, 2),
        (8, 4, 3, 0),
        (9, 4, 4, 1),
        (10, 4, 5, 2),
    },
    "limbo_publication":set(),
    "limbo_authors":set(),

}


test_limbo={
    "limbo_publication":{
        (1,'Reason.AMB_CLUSTER','key',"title","1-5",None,"doi",None,None,'2011','1990',"1","2","series",None,None,"publisher",None,"school","address",
         "isbn",None,"booktitle","journal")
    },
    "limbo_authors":{
        (1,1,'None',"An Author",0),
        (2,1,'None',"Another Author",1),
    },
    "publication_authors": set(),

}
test_limbo2={
    "limbo_publication":{
        (1,'Reason.AMB_PUB','key',"title","1-5",None,"doi",None,None,'2011','1990',"1","2","series",None,None,"publisher",None,"school","address",
         "isbn",None,"booktitle","journal")
    },
    "limbo_authors":{
        (1,1,'None',"An Author",0),
        (2,1,'None',"Another Author",1),
    },
    "publication_authors": set(),

}
"""
    "publication": {
        (1, 2, 1, None, "Bla Bla Bla", "1-5", None, "dummydoi", None, None, "2011", "1989", "1", "2"),
        (2, 4, 2, None, "Kam? Kim! Kum.", "10-11", None, "doidoi", None, None, "2014", "2014", "51", "8")
    },

"""


class TestIngsterDblp(TestCase):

    def test_invalid_ingester(self):
        setup_tables("dblp_test1.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        self.assertRaises(IIngester_Exception,ingest_data2,datetime.datetime(1990,1,1,1,1,1),TESTDB)

    def test_success(self):
        setup_tables("dblp_test1.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester(TESTDB, TESTDB)
        self.assertEqual(ingester.get_global_url(), 3)
        result = ingest_data2(ingester, TESTDB)
        self.assertEqual(result,2)
        compare_tables(self, test_success, ignore_id=True)
        tmp = list(get_table_data("dblp_article", null_dates=False))
        # check if last harvested is set
        self.assertEqual(tmp[0][-1].strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%Y-%m-%d"))

    def test_success_limit(self):
        setup_tables("dblp_test1.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester(TESTDB, TESTDB)
        ingester.set_limit(1)
        result = ingest_data2(ingester, TESTDB)
        self.assertEqual(result, 1)


    def test_setup_database(self):
        setup_database(TESTDB)
        setup_database(TESTDB)

    def test_complete_publication(self):
        # for this test a dataset with ALL ROWS filled, will be created to check if all values are
        # successfully transferred
        setup_tables("dblp_test2.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester(TESTDB, TESTDB)
        ingest_data2(ingester, TESTDB)
        publication = list(get_table_data("publication", TESTDB))[0]
        # remove diff tree for easier comparision
        filtered_pub = [publication[x] for x in range(len(publication)) if x != 3]

        # list of values that should be included in publication
        included_values= [1,2,1,"title","1-5",None,"doi",None,None,None, "1990",'1','2']
        self.assertEqual(filtered_pub,included_values)

    def test_limbo_multi_cluster(self):
        setup_tables("dblp_test2.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        insert_data("INSERT into cluster (id,cluster_name) VALUES(1,'title'),(2,'title')")
        ingester = DblpIngester(TESTDB, TESTDB)
        ingest_data2(ingester, TESTDB)
        compare_tables(self,test_limbo,ignore_id=True)

    def test_limbo_multi_pubs(self):
        setup_tables("dblp_test2.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        insert_data("INSERT into cluster (id,cluster_name) VALUES(1,'title')")
        insert_data("INSERT into global_url (id,domain,url) VALUES(5,'a','a')")
        insert_data("INSERT into local_url (id,url,global_url_id) VALUES(1,'a',5)")
        insert_data("INSERT into publication(id,url_id,cluster_id, title)VALUES (1,1,1,'title')")
        insert_data("INSERT into publication(id,url_id,cluster_id, title)VALUES (2,1,1,'title')")
        ingester = DblpIngester(TESTDB, TESTDB)
        ingest_data2(ingester, TESTDB)
        compare_tables(self, test_limbo2, ignore_id=True)

    def tearDown(self):
        delete_database(TESTDB)
        pass


