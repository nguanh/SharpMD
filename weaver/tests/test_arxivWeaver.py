from django.test import TransactionTestCase
from weaver.models import *
from mysqlWrapper.mariadb import MariaDb
from oai.queries import ARXIV_ARTICLE,ADD_ARXIV
from oai.arxivweaver import ArxivWeaver
import datetime


class TestArxivWeaver(TransactionTestCase):

    def setUp(self):
        self.check_query = "SELECT * FROM test_storage.arxiv_articles WHERE identifier = %s "
        #self.check_query ="SELECT * FROM test_storage.arxiv_articles"
        self.connector = MariaDb(db="test_storage")
        self.connector.createTable("Arxiv article", ARXIV_ARTICLE.format("InnoDB"))
        dataset1=("AAAAA", None, None, "Andrew Andrewsen; Bertha Berthasen;", "title1",
                  None, None, None, None, None, None, None, None,
                  datetime.datetime(1990, 1, 1, 1, 1, 1, 1))
        dataset2=("BBBBB", None, None, "BAndrew BAndrewsen; EBertha EBerthasen;", "title2",
                  None, None, None, None, None, None, None, None,
                  datetime.datetime(1990, 1, 1, 1, 1, 1, 1))
        self.connector.execute_ex(ADD_ARXIV, dataset1)
        self.connector.execute_ex(ADD_ARXIV, dataset2)

    def tearDown(self):
        self.connector.close_connection()

    def test_success(self):
        obj = ArxivWeaver(2,"test_storage")
        obj.run()

        link1 = PDFDownloadQueue.objects.get(id=1)
        link2 = PDFDownloadQueue.objects.get(id=2)
        self.assertEqual(link1.test(), ["https://arxiv.org/pdf/AAAAA.pdf",0,1])
        self.assertEqual(link2.test(), ["https://arxiv.org/pdf/BBBBB.pdf",0,2])

        source1 = OpenReferences.objects.get(id=1).test()
        source2 = OpenReferences.objects.get(id=2).test()
        self.assertEqual(source1,[0, "AAAAA", None])
        self.assertEqual(source2,[0,"BBBBB",None])

