from django.test import TransactionTestCase,mock
from dblp.dblpingester import DblpIngester
from ingester.models import global_url


class TestDblpIngest(TransactionTestCase):

    def test_success_create_global_url(self):
        self.assertEqual(global_url.objects.count(),0)
        x = DblpIngester("Hello")
        url = global_url.objects.get(id=1)
        self.assertEqual(url.domain,'http://dblp.uni-trier.de')
        self.assertEqual(x.get_global_url().id,1)
        self.assertEqual(x.harvester_db,"harvester")

    def test_success_update_global_url(self):
        global_url.objects.create(
            id="100",
            domain='http://dblp.uni-trier.de',
            url = 'http://dblp.uni-trier.de/rec/xml/'
        )
        x = DblpIngester("Hello")
        self.assertEqual(x.get_global_url().id,100)


