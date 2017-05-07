from django.test import TransactionTestCase
from conf.config import get_config
from mysqlWrapper.mariadb import MariaDb
from dblp.queries import DBLP_ARTICLE, ADD_DBLP_ARTICLE
from oai.queries import ARXIV_ARTICLE, ADD_ARXIV, ADD_OAI_DEFAULT,OAI_DATASET
from dblp.dblpingester import DblpIngester
from oai.arxivingester import ArxivIngester
from oai.citeseeringester import CiteseerIngester
from ingester.ingesting_function import ingest_data
from ingester.difference_storage import deserialize_diff_store
from weaver.models import OpenReferences
from ingester.models import *
import datetime
import os
test_path = os.path.dirname(__file__)
ingester_path = os.path.dirname(test_path)


class TestIngesterCiteseer(TransactionTestCase):
    fixtures = [os.path.join(ingester_path, "fixtures", "initial_data.json")]
    @classmethod
    def setUpClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex(("CREATE FULLTEXT INDEX cluster_ft_idx  ON test_storage.ingester_cluster (name)"), ())
        connector.execute_ex(
            "CREATE FULLTEXT INDEX authors_model_ft_idx ON test_storage.ingester_authors_model (block_name)", ())
        connector.close_connection()

    @classmethod
    def tearDownClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex("ALTER TABLE test_storage.ingester_cluster DROP INDEX cluster_ft_idx", ())
        connector.execute_ex("ALTER TABLE test_storage.ingester_authors_model DROP INDEX authors_model_ft_idx", ())
        connector.close_connection()

    def setUp(self):
        self.connector = MariaDb(db="test_storage")
        storage_engine = get_config("MISC")["storage_engine"]
        # create tables for both sources arxiv and dblp
        self.connector.createTable("citeseerarticle", OAI_DATASET.format(storage_engine))
        self.connector.createTable("dblparticle", DBLP_ARTICLE.format(storage_engine))
        self.connector.createTable("arxivarticle", ARXIV_ARTICLE.format(storage_engine))
        # insert data
        dblp_article = ("dblpkey",  # key
                        "2011-11-11",  # mdate
                        "Andreas Theodor Anders;Bertha Theresa Balte;",  # authors
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
                         "Andreas Theodor Anders;Bertha Theresa Balte;Carim Chass Jr.;",  # authors
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

        citeseer_article = ("citeseerkey",
                            "Andreas Theodor Anders;Bertha Theresa Balte;Carim Chass Jr.;",
                            "The ultimate Title;",
                            "A description;",
                            None, # contributor
                            None, # Coverage
                            "2008-08-08;2009-09-09;2010-10-10;", # dates
                            None, #format
                            None, # languages
                            None, # Publisher
                            None, # relation
                            None, # rights
                            None, # sources
                            "KeywordA;KeywordB;KeywordC;", # subject
                            None, # type
                            )

        self.connector.execute_ex(ADD_DBLP_ARTICLE, dblp_article)
        self.connector.execute_ex(ADD_ARXIV, arxiv_article)
        self.connector.execute_ex(ADD_OAI_DEFAULT,citeseer_article)

    def tearDown(self):
        self.connector.execute_ex("DROP TABLE test_storage.arxiv_articles")
        self.connector.execute_ex("DROP TABLE test_storage.dblp_article")
        self.connector.execute_ex("DROP TABLE test_storage.oaipmh_articles")
        self.connector.close_connection()

    def test_success_all_3_ingester(self):
        dblpingester = DblpIngester("dblp.ingester", harvesterdb="test_storage")
        arxivingester = ArxivIngester("arxiv.ingester", harvester_db="test_storage")
        citeseeringester = CiteseerIngester("citeseer.ingester",harvester_db="test_storage")

        # arxiv first then dblp
        result2 = ingest_data(arxivingester)
        self.assertEqual(result2, 1)
        result = ingest_data(dblpingester)
        self.assertEqual(result, 1)

        result3 = ingest_data(citeseeringester)
        self.assertEqual(result3,1)


        # check all tables
        self.assertEqual(cluster.objects.count(), 1)
        self.assertEqual(publication.objects.count(), 1)
        self.assertEqual(local_url.objects.count(), 4)
        self.assertEqual(global_url.objects.count(), 5)
        self.assertEqual(limbo_authors.objects.count(), 0)
        self.assertEqual(limbo_pub.objects.count(), 0)
        self.assertEqual(pub_medium.objects.count(), 1)
        # check local url
        dblp_url = local_url.objects.get(id=3)
        pub_url = local_url.objects.get(id=2)
        arxiv_url = local_url.objects.get(id=1)
        citeseerurl = local_url.objects.get(id=4)
        self.assertEqual(dblp_url.test(),
                         [3, "dblpkey", 1, publication_type.objects.get(name="article").id, None])
        self.assertEqual(arxiv_url.test(),
                         [4, "arxivkey", None, publication_type.objects.get(name="misc").id, None])
        self.assertEqual(pub_url.test(),
                         [1, "TODO PLATZHALTER", 1, publication_type.objects.get(name="misc").id, None])
        self.assertEqual(citeseerurl.test(), [5, "citeseerkey", None, publication_type.objects.get(name="misc").id, None])
        # check authors
        self.assertEqual(authors_model.objects.count(), 3)
        self.assertEqual(author_aliases.objects.count(), 3)
        self.assertEqual(author_alias_source.objects.count(), 8)
        # publication authors
        self.assertEqual(publication_author.objects.count(), 11)
        # check publication
        publ = publication.objects.first()
        self.assertEqual(publ.title, "The Ultimate Title!")  # from Arxiv
        self.assertEqual(publ.pages, "10-14")  # DBLP
        self.assertEqual(publ.note, None)
        self.assertEqual(publ.doi, "http://google.com")  # Arxiv
        self.assertEqual(publ.abstract, "this is a test")  # arxiv
        self.assertEqual(publ.copyright, None)
        self.assertEqual(publ.date_added, None)
        self.assertEqual(publ.date_published, datetime.date(2007, 1, 1))  # DBLP
        self.assertEqual(publ.volume, "2")  # DBLP
        self.assertEqual(publ.number, "3")  # DBLP
        # check diff tree
        diff = deserialize_diff_store(publ.differences)
        self.assertEqual(diff["url_id"], [1, 3, 4])
        self.assertEqual(diff["doi"], [{"bitvector": 1, "votes": 0, "value": "http://google.com"},
                                       {"bitvector": 2, "votes": 0, "value": "http://google.de"}])
        self.assertEqual(diff["copyright"], [])
        self.assertEqual(diff["type_ids"], [{"bitvector": 5, "votes": 0, "value": 2}, # arxiv and citeseer share value
                                            {"bitvector": 2, "votes": 0, "value": 1}])
        self.assertEqual(diff["pages"], [{"bitvector": 2, "votes": 0, "value": "10-14"}])

        # check keywords
        self.assertEqual(keywordsModel.objects.count(),3)
        self.assertEqual(keyword_aliases.objects.count(),3)
        self.assertEqual(keyword_alias_source.objects.count(),3)
        self.assertEqual(publication_keyword.objects.count(),6)

        self.assertEqual(OpenReferences.objects.first().test(), [1, 'arxivkey', None])








