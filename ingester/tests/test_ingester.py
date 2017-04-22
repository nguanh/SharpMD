from django.test import TransactionTestCase
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


class TestIngester(TransactionTestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]

    def setUp(self):
        self.connector = MariaDb(db="test_storage")
        storage_engine = get_config("MISC")["storage_engine"]
        self.connector.createTable("dblparticle", DBLP_ARTICLE.format(storage_engine))

    def tearDown(self):
        self.connector.execute_ex("DROP TABLE test_storage.dblp_article")
        self.connector.close_connection()

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
        self.assertEqual(local_url.objects.get(id=1).test(), [3, 'journals/acta/AkyildizB89', 1, 1,None])
        self.assertEqual(local_url.objects.get(id=2).test(), [1, 'TODO PLATZHALTER', 1, 1,None])
        self.assertEqual(local_url.objects.get(id=3).test(), [3, 'journals/acta/VoglerS014', 1, 1,None])
        self.assertEqual(local_url.objects.get(id=4).test(), [1, 'TODO PLATZHALTER', 1, 1,None])
        # check authors_model
        self.assertEqual(authors_model.objects.get(id=1).test(),["Ian F. Akyildiz", "ian f akyildiz"])
        self.assertEqual(authors_model.objects.get(id=2).test(), ["Horst von Brand", "horst von brand"])
        self.assertEqual(authors_model.objects.get(id=3).test(), ["Walter Vogler", "walter vogler"])
        self.assertEqual(authors_model.objects.get(id=4).test(), ["Christian Stahl", "christian stahl"])
        self.assertEqual(authors_model.objects.get(id=5).test(), ["Richard Müller", "richard muller"])
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

    def test_success_limit(self):
        setup_tables(os.path.join(test_path, "dblp_test1.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingester.set_limit(1)
        result = ingest_data(ingester)
        self.assertEqual(result, 1)

    def test_complete_publication(self):
        # for this test a dataset with ALL ROWS filled, will be created to check if all values are
        # successfully transferred
        setup_tables(os.path.join(test_path, "dblp_test2.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingest_data(ingester)
        publ = publication.objects.first()
        self.assertEqual(publ.title,"title")
        self.assertEqual(publ.pages, "1-5")
        self.assertEqual(publ.doi, "doi")
        self.assertEqual(publ.abstract, None)
        self.assertEqual(publ.copyright, None)
        self.assertEqual(publ.volume, "1")
        self.assertEqual(publ.number, "2")
        self.assertEqual(publ.note, None)
        self.assertEqual(publ.date_added, None)
        self.assertEqual(publ.date_published, datetime.date(1990,1,1))

    def test_limbo_multi_cluster(self):
        setup_tables(os.path.join(test_path, "dblp_test2.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        cluster.objects.bulk_create([
            cluster(id=1, name="title"),
            cluster(id=2, name="title"),
        ])
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingest_data(ingester)
        self.assertEqual(limbo_authors.objects.get(id=1).test(), [1, 'None', "An Author", 0])
        self.assertEqual(limbo_authors.objects.get(id=2).test(), [1, 'None', "Another Author", 1])
        self.assertEqual(local_url.objects.count(),0)
        limbo = limbo_pub.objects.get(id=1).test_extended()
        compare = ['Reason.AMB_CLUSTER','key',"title","1-5",None,"doi",None,None,
                                datetime.date(2011,1,1),datetime.date(1990,1,1),"1","2","series",
                                None,"publisher",None,"school","address",
                                "isbn",None,"booktitle","journal"]
        self.assertEqual(limbo,compare)

    def test_limbo_multi_pubs(self):
        setup_tables(os.path.join(test_path, "dblp_test2.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        cl = cluster.objects.create(id=1, name="title")
        gurl = global_url.objects.create(id=5,domain ="http://dummy.de", url="http://dummy.de")
        lurl = local_url.objects.create(id=1,url="jlkjöl", global_url=gurl)
        publication.objects.bulk_create([
            publication(url=lurl,cluster=cl,title="Title"),
            publication(url=lurl, cluster=cl, title="Title")
        ])
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingest_data(ingester)
        limbo = limbo_pub.objects.get(id=1).test_extended()
        self.assertEqual(limbo[0],'Reason.AMB_PUB')
        self.assertEqual(limbo_authors.objects.get(id=1).test(), [1, 'None', "An Author", 0])
        self.assertEqual(limbo_authors.objects.get(id=2).test(), [1, 'None', "Another Author", 1])
        self.assertEqual(local_url.objects.count(),1)

    def test_limbo_alias(self):
        setup_tables(os.path.join(test_path, "dblp_test3.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingest_data(ingester)

        self.assertEqual(limbo_pub.objects.count(), 0)
        self.assertEqual(cluster.objects.count(), 3)
        self.assertEqual(authors_model.objects.count(), 5)

    def test_set_last_harvested(self):
        setup_tables(os.path.join(test_path, "dblp_test3.csv"), DBLP_ARTICLE, ADD_DBLP_ARTICLE)
        ingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        ingester.set_limit(1)
        result1 = ingest_data(ingester)
        self.assertEqual(result1, 1)
        ingester.set_limit(3)
        result2 = ingest_data(ingester)
        self.assertEqual(result2, 2)




