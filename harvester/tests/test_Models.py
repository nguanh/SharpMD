

from harvester.models import Schedule, IntervalSchedule, PeriodicTask, Config
from django.test import TestCase, mock
import json
import datetime


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
            task="harvester.tasks.test",
            schedule= self.schedule,
            extra_config={"a":1}
        )

    def test_new_celery_task(self):
        test = Config.objects.create(
            id=self.config_id +1,
            name="Test Harvester2",
            table_name="Test_Table",
            enabled=True,
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule=self.schedule,
            extra_config={"a": 1}
        )
        task = test.celery_task
        self.assertNotEqual(test.name,task.name)
        self.assertEqual(test.schedule.schedule,task.interval)
        self.assertEqual(test.task,task.task)
        self.assertEqual(task.args,json.dumps(["dblp.dblpharvester","DblpHarvester",self.config_id+1]))

    def test_update_celery_task(self):
        self.config.name = "New Harvester"
        self.config.task = "harvester.tasks.harvestsource"
        self.config.module_path = "newpath"
        self.config.module_name = "newname"
        self.config.save()
        task = self.config.celery_task
        self.assertEqual(task.name, "New Harvester-Task")
        self.assertEqual(task.args,json.dumps(["newpath","newname",self.config_id]))
        self.assertEqual(task.task,self.config.task)

    def test_time_interval_all(self):
        schedule,created = Schedule.objects.get_or_create(
            name="test_schedule1",
            time_interval= "all",
            schedule= self.interval,

        )
        test = Config.objects.create(
            id=self.config_id +1,
            name="Test Harvester2",
            table_name="Test_Table",
            enabled=True,
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule=schedule,
            extra_config={"a": 1}
        )

        test.save()
        self.assertEqual(test.start_date, None)
        self.assertEqual(test.end_date, None)

    def test_time_interval_monthly(self):
        schedule, created = Schedule.objects.get_or_create(
            name="test_schedule1",
            time_interval="month",
            schedule=self.interval,
            min_date = datetime.date(2011,5,1),
            max_date = datetime.date(2012,1,1),

        )
        test = Config.objects.create(
            id=self.config_id + 1,
            name="Test Harvester2",
            table_name="Test_Table",
            enabled=True,
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule=schedule,
            extra_config={"a": 1}
        )

        test.save()
        self.assertEqual(test.start_date, datetime.date(2011,5,1))
        self.assertEqual(test.end_date, datetime.date(2011,5,31))

    def test_time_interval_weekly_max_date(self):
        schedule, created = Schedule.objects.get_or_create(
            name="test_schedule1",
            time_interval="week",
            schedule=self.interval,
            min_date=datetime.date(2011, 5, 1),
            max_date=datetime.date(2011, 5, 3),

        )
        test = Config.objects.create(
            id=self.config_id + 1,
            name="Test Harvester2",
            table_name="Test_Table",
            enabled=True,
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule=schedule,
            extra_config={"a": 1}
        )

        test.save()
        self.assertEqual(test.start_date, datetime.date(2011, 5, 1))
        self.assertEqual(test.end_date, datetime.date(2011, 5, 3))

    def test_time_interval_daily(self):
        schedule, created = Schedule.objects.get_or_create(
            name="test_schedule1",
            time_interval="day",
            schedule=self.interval,
            min_date=datetime.date(2011, 5, 1),
            max_date=datetime.date(2011, 5, 3),

        )
        test = Config.objects.create(
            id=self.config_id + 1,
            name="Test Harvester2",
            table_name="Test_Table",
            enabled=True,
            url="http://google.de",
            module_path="dblp.dblpharvester",
            module_name="DblpHarvester",
            task="harvester.tasks.test",
            schedule=schedule,
            extra_config={"a": 1}
        )

        test.save()
        self.assertEqual(test.start_date, datetime.date(2011, 5, 1))
        self.assertEqual(test.end_date, datetime.date(2011, 5, 2))





