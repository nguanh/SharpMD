
from harvester.IHarvester import IHarvest
from harvester.exception import IHarvest_Exception, IHarvest_Disabled
from harvester.models import Schedule, IntervalSchedule,PeriodicTask,Config
from oai.oaiharvester import OaiHarvester
from django.test import TestCase, mock



class TestIHarvest(TestCase):
    def setUp(self):
        # create IntervalSchedule
        self.config_id = 100
        self.interval, created = IntervalSchedule.objects.get_or_create(
                every = 10,
                period = IntervalSchedule.SECONDS)
        # create schedule
        self.schedule,created = Schedule.objects.get_or_create(
            name="test_schedule",
            time_interval= "all",
            schedule= self.interval,
        )

        # create periodic task
        self.periodic,created = PeriodicTask.objects.get_or_create(
            name="test",
            interval=self.interval,
            task="harvester.tasks.test"
        )

        self.config,created = Config.objects.get_or_create(
            id=self.config_id,
            name= "Test Harvester",
            table_name ="Test_Table",
            enabled = True,
            url="http://citeseerx.ist.psu.edu/oai2",
            module_path="oai.oaiharvester",
            module_name="oaiHarvester",
            task="harvester.tasks.test",
            schedule= self.schedule,
        )

    def test_success(self):
        x = OaiHarvester(self.config_id)
        self.assertEqual(x.table_name,"Test_Table")
        self.assertEqual(x.url,"http://citeseerx.ist.psu.edu/oai2")

    def test_valid_init(self,func,func2):
        x = OaiHarvester(self.config_id)
        self.assertEqual(x.init(), True)

    def test_cleanup(self):
        x = OaiHarvester(self.config_id)
        self.assertTrue(x.connector.connector.is_connected())
        x.cleanup()
        self.assertFalse(x.connector.connector.is_connected())







