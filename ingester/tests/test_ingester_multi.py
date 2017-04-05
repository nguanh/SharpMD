from django.test import TestCase, TransactionTestCase
from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from dblp.queries import DBLP_ARTICLE, ADD_DBLP_ARTICLE
from oai.queries import ARXIV_ARTICLE, ADD_ARXIV
from dblp.dblpingester import DblpIngester
from ingester.ingesting_function import ingest_data
from ingester.exception import IIngester_Exception
from ingester.models import *
from .ingester_tools import setup_tables, get_table_data
import datetime
import os
test_path = os.path.dirname(__file__)
ingester_path = os.path.dirname(test_path)


class TestIngesterMulti(TransactionTestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]

    def setUp(self):
        self.connector = MariaDb(db="test_storage")
        storage_engine = get_config("MISC")["storage_engine"]
        # create tables for both sources arxiv and dblp
        self.connector.createTable("dblparticle", DBLP_ARTICLE.format(storage_engine))
        self.connector.createTable("arxivarticle", ARXIV_ARTICLE.format(storage_engine))
        # insert data
        dblp_article = ("dblpkey",  # key
                        "2011-11-11",  # mdate
                        "Andreas Anders; Bertha Theresa Balte; Carim Chass Jr.;",  # authors
                        "The Ultimate Title",  # title
                        "10-14",  # pages
                        datetime.date(2005,1,1),  # pub year
                        "2",  # volume
                        "journal of stuff",  # journal
                        "3",  # journal number
                        "http://google.de",  # doi
                        "http://unused.com", # unused url
                        None,  # cite
                        None,  # crossref
                        None,  # booktitle
                        None,  # school
                        None,  # address
                        None,  # publisher
                        None,  # isbn
                        None,  # series
                        "article"  # type
                        )

        arxiv_article = ("arxivkey",  # identifier
                         "2007-07-07",  # created
                         "2008-08-08",  # updated
                         "Andreas Theodor Anders; Bertha Theresa Balte;",  # authors
                         "The Ultimate Title!",  # title
                         None,  # mscclass
                         None,  # acmclass
                         None,  # reportno
                         None,  # journalref
                         None,  # comments
                         "this is a test",  # description
                         "category",  # categories
                         "http://google.com",  # doi
                         "2009-09-09"  # mdate
                        )

        self.connector.execute_ex(ADD_DBLP_ARTICLE, dblp_article)
        self.connector.execute_ex(ADD_ARXIV, arxiv_article)
        self.connector.close_connection()
    """
    def tearDown(self):
        self.connector.execute_ex("DROP TABLE test_storage.dblp_article")
        self.connector.close_connection()
    """

    def test_success_multi(self):
        # ingest dblp first
        dblpingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        result = ingest_data(dblpingester)
        self.assertEqual(result,1)
        # then arxiv