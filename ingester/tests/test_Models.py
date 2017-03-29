

from ingester.models import IntervalSchedule, PeriodicTask, Config
from django.test import TestCase, mock
import json
import datetime


class TestIngestModel(TestCase):
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

    def test_new_ingester_task(self):
        test = Config.objects.create(
            id=self.config_id +1,
            name="Test ingester",
            enabled=True,
            module_path="dblp.dblpingester",
            module_name="DblpIngester",
            schedule=self.interval,
            limit = 100
        )
        task = test.ingester_task
        self.assertNotEqual(test.name,task.name)
        self.assertEqual(test.schedule,task.interval)
        self.assertEqual("ingester.tasks.ingestsource",task.task)
        self.assertEqual(task.args,json.dumps(["dblp.dblpingester","DblpIngester",self.config_id+1]))

    def test_update_celery_task(self):
        self.config.name = "New Ingester"
        self.config.module_path = "newpath"
        self.config.module_name = "newname"
        self.config.save()
        task = self.config.ingester_task
        self.assertEqual(task.name, "New Ingester-Task")
        self.assertEqual(task.args, json.dumps(["newpath","newname",self.config_id]))


