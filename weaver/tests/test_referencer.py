from django.test import TransactionTestCase
from weaver.models import *
from ingester.models import *
from weaver.Referencer import Referencer
import os
from mysqlWrapper.mariadb import MariaDb
from datetime import date


class TestReferencer(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex(("CREATE FULLTEXT INDEX cluster_ft_idx  ON test_storage.ingester_cluster (name)"), ())
        connector.close_connection()

    @classmethod
    def tearDownClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex("ALTER TABLE test_storage.ingester_cluster DROP INDEX cluster_ft_idx", ())
        connector.close_connection()

    def setUp(self):
        old_date = date(2000, 1, 1)
        # setup ingester models
        self.gurl = global_url.objects.create(id= 5, domain="http://dummy.de", url="http://dummy.de")
        self.url1 = local_url.objects.create(id=1, url="url1", global_url=self.gurl)
        self.url2 = local_url.objects.create(id=2, url="url2", global_url=self.gurl)
        self.url3 = local_url.objects.create(id=3, url="url3", global_url=self.gurl)

        self.cluster1 = cluster.objects.create(name="specialized research datasets in the citeseerx digital library")
        self.cluster2 = cluster.objects.create(name="pattern recognition and machine learning ")
        self.cluster3 = cluster.objects.create(name="collabseer a search engine for collaboration discovery")

        #setup weaver models
        self.op1 = OpenReferences.objects.create(source_table=1,
                                                 source_key="test1",
                                                 ingester_key=self.url1)
        self.op2 = OpenReferences.objects.create(source_table=1,
                                                 source_key="test2",
                                                 ingester_key=self.url2)
        self.op3 = OpenReferences.objects.create(source_table=1,
                                                 source_key="test3",
                                                 ingester_key=self.url3)
        # titles are copied from a grobid parsing session
        self.single11 = SingleReference.objects.create(source=self.op1,
                                                       title="Specialized research datasets in the CiteSeerX digital library",
                                                       authors=bytes(4))
        self.single21 = SingleReference.objects.create(source=self.op2,
                                                       title="Pattern Recognition and Machine Learning (Information Science and Statistics",
                                                       authors=bytes(4))
        self.single22 = SingleReference.objects.create(source=self.op2, title="Citeseerx: A scholarly big dataset", authors=bytes(4))
        self.single31 = SingleReference.objects.create(source=self.op3,
                                                       title="Layout and content extraction for pdf documents",
                                                       authors=bytes(4))
        self.single32 = SingleReference.objects.create(source=self.op3,
                                                       title="Figure metadata extraction from digital documents",
                                                       authors=bytes(4))
        self.single33 = SingleReference.objects.create(source=self.op3,
                                                       title="Collabseer: a search engine for collaboration discovery",
                                                       authors=bytes(4))

    def test_success(self):
        ref = Referencer(limit=2)
        self.assertEqual(PubReference.objects.count(), 0)
        self.assertEqual(SingleReference.objects.count(),6)
        ref.run()
        self.assertEqual(PubReference.objects.count(),1)
        self.assertEqual(SingleReference.objects.count(),5)
        self.assertEqual(PubReference.objects.get(id=1).test(), [1, 1])
