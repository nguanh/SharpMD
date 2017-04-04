from django.test import TestCase
from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from dblp.queries import DBLP_ARTICLE, ADD_DBLP_ARTICLE
from dblp.dblpingester import DblpIngester
from ingester.ingesting_function import ingest_data
from ingester.exception import IIngester_Exception
from ingester.models import *
from .ingester_tools import setup_tables, get_table_data
import datetime
import os
test_path = os.path.dirname(__file__)
ingester_path = os.path.dirname(test_path)

#TODO weitere tabellen hinzufügen

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


class TestIngesterDblp(TestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]

    def setUp(self):
        connector = MariaDb(db="test_storage")
        storage_engine = get_config("MISC")["storage_engine"]
        connector.createTable("dblparticle", DBLP_ARTICLE.format(storage_engine))

    def test_invalid_ingester(self):
        setup_tables(os.path.join(test_path, "dblp_test1.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        self.assertRaises(IIngester_Exception, ingest_data, datetime.datetime(1990,1,1,1,1,1))

    def test_success(self):
        setup_tables(os.path.join(test_path, "dblp_test1.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        self.assertEqual(ingester.get_global_url().id, 3)
        result = ingest_data(ingester)
        self.assertEqual(result, 2)
        # check local url
        self.assertEqual(local_url.objects.get(id=1).test(), [3, 'journals/acta/AkyildizB89', 1, 1])
        self.assertEqual(local_url.objects.get(id=2).test(), [1, 'TODO PLATZHALTER', 1, 1])
        self.assertEqual(local_url.objects.get(id=3).test(), [3, 'journals/acta/VoglerS014', 1, 1])
        self.assertEqual(local_url.objects.get(id=4).test(), [1, 'TODO PLATZHALTER', 1, 1])
        # check authors_model
        self.assertEqual(authors_model.objects.get(id=1).test(),["Ian F. Akyildiz", "akyildiz,i"])
        self.assertEqual(authors_model.objects.get(id=2).test(), ["Horst von Brand", "von brand,h"])
        self.assertEqual(authors_model.objects.get(id=3).test(), ["Walter Vogler", "vogler,w"])
        self.assertEqual(authors_model.objects.get(id=4).test(), ["Christian Stahl", "stahl,c"])
        self.assertEqual(authors_model.objects.get(id=5).test(), ["Richard Müller", "muller,r"])
        # check author alias
        self.assertEqual(author_aliases.objects.get(id=1).test(), [1, "Ian F. Akyildiz"])
        self.assertEqual(author_aliases.objects.get(id=2).test(), [2, "Horst von Brand"])
        self.assertEqual(author_aliases.objects.get(id=3).test(), [3, "Walter Vogler"])
        self.assertEqual(author_aliases.objects.get(id=4).test(), [4, "Christian Stahl"])
        self.assertEqual(author_aliases.objects.get(id=5).test(), [5, "Richard Müller 0001"])
        self.assertEqual(author_aliases.objects.get(id=6).test(), [5, "Richard Müller"])
        # cluster
        self.assertEqual(cluster.objects.get(id=1).name, "bla bla bla")
        self.assertEqual(cluster.objects.get(id=2).name, "kam kim kum")
        # author alias source
        self.assertEqual(author_alias_source.objects.get(id=1).test(), [1, 1])
        self.assertEqual(author_alias_source.objects.get(id=2).test(), [2, 1])
        self.assertEqual(author_alias_source.objects.get(id=3).test(), [3, 3])
        self.assertEqual(author_alias_source.objects.get(id=4).test(), [4, 3])
        self.assertEqual(author_alias_source.objects.get(id=5).test(), [5, 3])
        self.assertEqual(author_alias_source.objects.get(id=6).test(), [6, 3])
        # publication authors
        self.assertEqual(publication_author.objects.get(id=1).test(), [1, 1, 0])
        self.assertEqual(publication_author.objects.get(id=2).test(), [1, 2, 1])
        self.assertEqual(publication_author.objects.get(id=3).test(), [2, 1, 0])
        self.assertEqual(publication_author.objects.get(id=4).test(), [2, 2, 1])
        self.assertEqual(publication_author.objects.get(id=5).test(), [3, 3, 0])
        self.assertEqual(publication_author.objects.get(id=6).test(), [3, 4, 1])
        self.assertEqual(publication_author.objects.get(id=7).test(), [3, 5, 2])
        self.assertEqual(publication_author.objects.get(id=8).test(), [4, 3, 0])
        self.assertEqual(publication_author.objects.get(id=9).test(), [4, 4, 1])
        self.assertEqual(publication_author.objects.get(id=10).test(), [4, 5, 2])

        # limbo
        self.assertEqual(limbo_authors.objects.count(),0)
        self.assertEqual(limbo_pub.objects.count(),0)

        # publication
        self.assertEqual(publication.objects.get(id=1).test(), [2, 1, "Bla Bla Bla"])
        self.assertEqual(publication.objects.get(id=2).test(), [4, 2, "Kam? Kim! Kum."])
        # check if last harvested is set
        tmp = list(get_table_data("dblp_article", null_dates=False))
        self.assertEqual(tmp[0][-1].strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%Y-%m-%d"))


"""
    def test_success_limit(self):
        setup_tables("dblp_test1.csv", DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester(TESTDB, TESTDB)
        ingester.set_limit(1)
        result = ingest_data2(ingester, TESTDB)
        self.assertEqual(result, 1)

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
"""

