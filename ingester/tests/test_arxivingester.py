from django.test import TransactionTestCase,mock
from oai.arxivingester import ArxivIngester
from ingester.models import global_url


class TestArxivIngest(TransactionTestCase):

    def test_success_create_global_url(self):
        self.assertEqual(global_url.objects.count(),0)
        x = ArxivIngester("Hello")
        url = global_url.objects.get(id=1)
        self.assertEqual(url.domain,'http://arxiv.org')
        self.assertEqual(x.get_global_url().id,1)
        self.assertEqual(x.harvester_db,"harvester")

    def test_success_update_global_url(self):
        global_url.objects.create(
            id="100",
            domain='http://arxiv.org',
            url = 'http://arxiv.org/abs/'
        )
        x = ArxivIngester("Hello")
        self.assertEqual(x.get_global_url().id,100)

    def test_set_harvester(self):
        x = ArxivIngester("Hello", "newdb")
        self.assertEqual(x.harvester_db,"newdb")


