from harvester.harvest_task import harvest_task
from harvester.exception import IHarvest_Disabled,IHarvest_Exception
from harvester.IHarvester import IHarvest
from django.test import TestCase, mock
from harvester.models import Schedule,PeriodicTask, IntervalSchedule, Config
import datetime


class MockHarvester(IHarvest):
    def __init__(self,config_id):
        pass

    def init(self):
        return True

    def run(self):
        pass
    def cleanup(self):
        pass


class TestHarvest_task(TestCase):

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
            url="http://test.de/",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule= self.schedule,
            extra_config={"zip_name": "dblp.xml.gz",
                          "dtd_name": "dblp.dtd",
                          "xml_name": "dblp.xml",
                          "extraction_path": "C:\\Users\\anhtu\\",
                          "tags":["a","b","c"]
                          }
        )

    def test_invalid_config_id(self):
        self.assertRaises(IHarvest_Exception,harvest_task,"harvester.tests.test_harvest_task", "MockHarvester", 0)

    def test_import_fail(self):
        self.assertRaises(ImportError, harvest_task, "dblp.dblpharXXXX", "DblpHarvester",self.config_id)

    def test_task_disabled(self):
        self.config.enabled = False
        self.config.save()
        self.assertRaises(IHarvest_Disabled, harvest_task, "dblp.dblpharvester", "DblpHarvester", self.config_id)

    def test_invalid_instance_fail(self):
        self.assertRaises(IHarvest_Exception, harvest_task, "harvester.exception", "IHarvest_Disabled", self.config_id)

    def test_instance_fail(self):
        # invalid extraction path
        self.config.extra_config["extraction_path"] = "blubb"
        self.config.save()
        self.assertRaises(IHarvest_Exception, harvest_task, "dblp.dblpharvester", "DblpHarvester", self.config_id)

    def test_success(self):
        # schedule interval is all
        self.assertTrue(harvest_task("harvester.tests.test_harvest_task", "MockHarvester", self.config_id))
        self.assertIsNone(self.config.start_date)
        self.assertIsNone(self.config.end_date)
        newconfig = Config.objects.get(id=self.config_id)
        self.assertEqual(newconfig.enabled,False)


    def test_monthly(self):
        schedule,created = Schedule.objects.get_or_create(
            name="test_schedule",
            time_interval= "month",
            schedule= self.interval,
            min_date = datetime.date(2011,1,1),
            max_date = datetime.date(2011,3,1),
        )
        self.config.schedule = schedule
        self.config.save()
        self.assertTrue(harvest_task("harvester.tests.test_harvest_task", "MockHarvester", self.config_id))
        newconfig = Config.objects.get(id=self.config_id)
        self.assertEqual(newconfig.start_date,datetime.date(2011,2,1))
        self.assertEqual(newconfig.end_date, datetime.date(2011,3,1))

    def test_monthly_limited(self):
        schedule,created = Schedule.objects.get_or_create(
            name="test_schedule",
            time_interval= "month",
            schedule= self.interval,
            min_date = datetime.date(2011,1,1),
            max_date = datetime.date(2011,1,25),
        )
        self.config.schedule = schedule
        self.config.save()
        self.assertTrue(harvest_task("harvester.tests.test_harvest_task", "MockHarvester", self.config_id))
        newconfig = Config.objects.get(id=self.config_id)
        self.assertEqual(newconfig.start_date,datetime.date(2011,1,26))
        self.assertEqual(newconfig.end_date, datetime.date(2011,1,25))


    def test_weekly_cacading(self):
        schedule,created = Schedule.objects.get_or_create(
            name="test_schedule",
            time_interval= "week",
            schedule= self.interval,
            min_date = datetime.date(2011,1,1),
            max_date = datetime.date(2011,3,1),
        )
        self.config.schedule = schedule
        self.config.save()
        harvest_task("harvester.tests.test_harvest_task", "MockHarvester", self.config_id)
        harvest_task("harvester.tests.test_harvest_task", "MockHarvester", self.config_id)
        newconfig = Config.objects.get(id=self.config_id)
        self.assertEqual(newconfig.start_date,datetime.date(2011,1,17))
        self.assertEqual(newconfig.end_date, datetime.date(2011,1,24))
