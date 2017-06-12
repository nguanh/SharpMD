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
        publication.objects.create(id=1, local_url=self.lurl, cluster=single, title="hi")

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
        self.assertEqual(result, ["lorem ipsum dolor"])

    def test_match2_no_results(self):
        cluster.objects.create(id=1, name="lorem ipsum dolor title")
        cluster.objects.create(id=2, name="lorem hababhu maklu title")
        cluster.objects.create(id=3, name="dolor maraku rtrua title")
        cluster.objects.create(id=4, name="dolor maraku rtrua title lorem")
        cluster.objects.create(id=5, name="lorem ipsum dor")
        cluster.objects.create(id=6, name="lorem ipsum dolor")
        result = [obj.name for obj in search_title("funny bunny")]
        self.assertEqual(result, [])




    def test_regression(self):
        cluster.objects.create(id=1, name="shrec10 track nonrigid 3d shape retrieval")
        cluster.objects.create(id=2, name="shrec 11 track shape retrieval on nonrigid 3d watertight meshes")
        cluster.objects.create(id=3, name="retrieval of nonrigid textured shapes using low quality 3d models")
        cluster.objects.create(id=4, name="canonical forms for nonrigid 3d shape retrieval")
        result = [obj.name for obj in search_title("Non-rigid 3D Shape Retrieval.") if obj is not None]
        self.assertEqual(len(result),2)

    def test_regression_2(self):
        cluster.objects.create(id=1, name="high temperature bonding solutions enabling thin wafer process and handling on 3dic manufacturing")
        result = search_title("TSV process solution for 3D-IC.")
        print(result)

    def test_regression_3(self):
        title = normalize_title("Physical activity 153 and incidence of coronary heart disease in middle-aged women Relative weight gain and obesity as a child predict metabolic and men")
        cluster.objects.create(id=1, name=title)
        result = search_title("Physical activity and incidence of coronary heart disease in middle-aged women and men.")
        # test fails so far
        self.assertEqual(len(result), 1)

    def test_regression_4(self):
        title = normalize_title("Beneficial effects of quercetin on sperm parameters in streptozotocin induced diabetic male rats")
        cluster.objects.create(id=1, name=title)
        result = search_title("Beneficial effects of quercetin on sperm parameters in streptozotocin‐induced diabetic male rats")
        # test fails so far
        self.assertEqual(len(result), 1)


    def test_match_limit(self):
        cluster.objects.create(id=1, name="lorem ipsum dolor title")
        cluster.objects.create(id=2, name="lorem ipsum title")
        cluster.objects.create(id=3, name="dolor lorem")
        cluster.objects.create(id=4, name="dolor lorem")
        cluster.objects.create(id=5, name="lorem ipsum dor")
        cluster.objects.create(id=6, name="lorem ipsum dolor")
        result = [obj.name for obj in search_title("lorem",threshold=0, limit=5)]
        self.assertEqual(len(result), 5)

    def test_regression_3(self):
        cluster.objects.create(id=1, name="lorem ipsum dolor")
        result = [obj.name for obj in search_title("lorem ipsum dolores",threshold=0.5, limit=5)]
        self.assertEqual(len(result), 1)