from django.test import TransactionTestCase,mock
from oai.citeseeringester import CiteseerIngester
from ingester.models import global_url


class TestCiteseerIngest(TransactionTestCase):

    def test_success_create_global_url(self):
        self.assertEqual(global_url.objects.count(),0)
        x = CiteseerIngester("Hello")
        url = global_url.objects.get(id=1)
        self.assertEqual(url.domain,'http://citeseerx.ist.psu.edu/')
        self.assertEqual(x.get_global_url().id,1)
        self.assertEqual(x.harvester_db,"harvester")

    def test_success_update_global_url(self):
        global_url.objects.create(
            id="100",
            domain='http://citeseerx.ist.psu.edu/',
            url = 'http://citeseerx.ist.psu.edu/viewdoc/summary?doi='
        )
        x = CiteseerIngester("Hello")
        self.assertEqual(x.get_global_url().id,100)

    def test_set_harvester(self):
        x = CiteseerIngester("Hello", "newdb")
        self.assertEqual(x.harvester_db,"newdb")


