from django.test import TestCase,TransactionTestCase

from ingester.helper import *
from ingester.matching_functions import match_title2
from ingester.matching_functions import search_title
from ingester.models import cluster, publication, global_url, local_url
from mysqlWrapper.mariadb import MariaDb


class TestMatchTitle2(TransactionTestCase):
    @classmethod
    def setUpClass(cls):
        connector = MariaDb(db="test_storage")
        connector.execute_ex(("CREATE FULLTEXT INDEX cluster_ft_idx  ON test_storage.ingester_cluster (name)"), ())
        connector.close_connection()

    def setUp(self):
        self.gurl = global_url.objects.create(id=5, domain="http://dummy.de", url="http://dummy.de")
        self.lurl = local_url.objects.create(id=1, url="blabla", global_url=self.gurl)

    def test_success_empty_db(self):

        result = match_title2("Single Title")
        self.assertEqual(result, {
                "status": Status.SAFE,
                "match": Match.NO_MATCH,
                "id": None,
                "reason": None,
            })

    def test_multi_cluster_match(self):
        cluster.objects.bulk_create([
            cluster(id=1, name="multi title"),
            cluster(id=2, name="multi title"),
        ])

        result = match_title2("Multi Title")
        self.assertEqual(result, {
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_CLUSTER,
            })

    def test_single_cluster_single_pub(self):
        multi = cluster.objects.create(id=1, name="multi title")
        single = cluster.objects.create(id=2, name="single title")
        publication.objects.create(id=1, url=self.lurl, cluster=single, title="hi")

        result = match_title2("single Title")
        self.assertEqual(result, {
                "status": Status.SAFE,
                "match": Match.SINGLE_MATCH,
                "id": single,
                "reason": None,
            })

    def test_single_cluster_multi_no_pub(self):
        cluster.objects.create(id=1, name="multi title")
        cluster.objects.create(id=2, name="single title")
        # no publications for cluster, why so ever
        result = match_title2("single Title")
        self.assertEqual(result, {
                "status": Status.LIMBO,
                "match": Match.MULTI_MATCH,
                "id": None,
                "reason": Reason.AMB_PUB,
            })

    def test_match2(self):
        cluster.objects.create(id=1, name="lorem ipsum dolor title")
        cluster.objects.create(id=2, name="lorem hababhu maklu title")
        cluster.objects.create(id=3, name="dolor maraku rtrua title")
        cluster.objects.create(id=4, name="dolor maraku rtrua title lorem")
        cluster.objects.create(id=5, name="lorem ipsum dor")
        cluster.objects.create(id=6, name="lorem ipsum dolor")
        result = [obj.name for obj in search_title("lorem ipsum dolor")]
        self.assertEqual(result, ["lorem ipsum dolor title", "lorem ipsum dolor"])

    def test_match2_no_results(self):
        cluster.objects.create(id=1, name="lorem ipsum dolor title")
        cluster.objects.create(id=2, name="lorem hababhu maklu title")
        cluster.objects.create(id=3, name="dolor maraku rtrua title")
        cluster.objects.create(id=4, name="dolor maraku rtrua title lorem")
        cluster.objects.create(id=5, name="lorem ipsum dor")
        cluster.objects.create(id=6, name="lorem ipsum dolor")
        result = [obj.name for obj in search_title("funny bunny")]
        self.assertEqual(result, [])
