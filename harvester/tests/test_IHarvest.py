
from harvester.IHarvester import IHarvest
from harvester.exception import IHarvest_Exception, IHarvest_Disabled
from harvester.models import Schedule, IntervalSchedule,PeriodicTask,Config
from django.test import TestCase, mock


class H1 (IHarvest):
    def __init__(self,config_id):
        IHarvest.__init__(self, config_id)

    def init(self):
        pass

    def run(self):
        pass

    def cleanup(self):
        pass

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
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            schedule= self.schedule,
            extra_config={"a":1}
        )

    def test_success(self):
        x = H1(self.config_id)
        self.assertEqual(x.name, "Test Harvester")
        self.assertEqual(x.table_name, "Test_Table")
        self.assertEqual(x.enabled,True)
        self.assertEqual(x.url,"http://google.de")
        self.assertEqual(x.limit,None)
        self.assertEqual(x.extra ,{"a":1})
        self.assertEqual(x.start_date,None)
        self.assertEqual(x.end_date,None)
        self.assertIsNotNone(x.connector)

    def test_not_enabled(self):
        self.config.enabled = False
        self.config.save()
        self.assertRaises(IHarvest_Disabled, H1,self.config_id)

    @mock.patch("harvester.IHarvester.MariaDb", side_effect= IHarvest_Exception())
    def test_no_connection(self, mock_stuff):
        self.assertRaises(IHarvest_Exception,H1,self.config_id)



