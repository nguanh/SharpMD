from django.test import TestCase,mock, TransactionTestCase
from ingester.ingest_task import ingest_task
from ingester.exception import IIngester_Exception, IIngester_Disabled
from ingester.models import IntervalSchedule,Config,PeriodicTask
from ingester.Iingester import Iingester


class mockIngester(Iingester):
    def __init__(self, name):
        self.name = name
        pass

    def get_global_url(self):
        pass

    def update_harvested(self):
        pass

    def mapping_function(self, query_dataset):
        pass


class TestIngestTask(TransactionTestCase):
    def setUp(self):
        # create IntervalSchedule
        self.config_id = 100
        self.interval, created = IntervalSchedule.objects.get_or_create(
                every = 10,
                period = IntervalSchedule.SECONDS)

        # create periodic task
        self.periodic,created = PeriodicTask.objects.get_or_create(
            name="test",
            interval=self.interval,
            task="harvester.tasks.test"
        )

        self.config,created = Config.objects.get_or_create(
            id=self.config_id,
            name= "Test Harvester",
            enabled = True,
            module_path="dblp.dblpingester",
            module_name="DblpIngester",
            schedule= self.interval,
        )

    def test_invalid_config_id(self):
        self.assertRaises(IIngester_Exception,ingest_task,"ingester.tests.test_ingest_task","mockIngester",self.config_id-1)

    def test_invalid_module(self):
        self.assertRaises(AttributeError,ingest_task,"dblp.dblpingester","DblpInester", self.config_id)

    def test_invalid_module_path(self):
        self.assertRaises(ImportError,ingest_task,"dblp.dblpingestr","DblpIngester", self.config_id)

    def test_invalid_module_class(self):
        self.assertRaises(IIngester_Exception, ingest_task,"harvester.exception", "IHarvest_Disabled", self.config_id)

    def test_disabled(self):
        self.config.enabled = False
        self.config.save()
        self.assertRaises(IIngester_Disabled, ingest_task,"ingester.tests.test_ingest_task","mockIngester",self.config_id)

    @mock.patch("ingester.ingest_task.ingest_data", return_value=5)
    def test_success(self,ingest_data_function):
        self.assertTrue(ingest_task("ingester.tests.test_ingest_task","mockIngester",self.config_id))


