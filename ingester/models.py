from __future__ import absolute_import, unicode_literals
from django.db import models
from django_celery_beat.models import PeriodicTask,IntervalSchedule
import jsonfield
import json

class Config(models.Model):
    # Name of the harvester for identification
    # name of harvester for logger
    name = models.CharField(max_length=200, unique=True)
    # amount of publications added per harvest
    limit = models.IntegerField(default=None, blank=True, null=True)
    enabled = models.BooleanField(default=True)
    module_path = models.CharField(max_length=200, default=None)
    module_name = models.CharField(max_length=200, default=None)
    schedule = models.ForeignKey(IntervalSchedule, default=None)
    # task is not visible on creation
    ingester_task = models.ForeignKey(PeriodicTask, default=None, null=True, blank=True,
                                      related_name="ingester_task", on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        # save object to get its id
        # pass config id as third task parameter
        if self.id is None:
            super(Config, self).save(*args, **kwargs)  # Call the "real" save() method.

        # join module path,name and id
        id_pass = [self.module_path,self.module_name,self.id]
        task_name = "ingester.tasks.ingestsource"
        if self.ingester_task is not None:
            setattr(self.ingester_task, 'name', "{}-Task".format(self.name))
            setattr(self.ingester_task, 'interval', self.schedule)
            setattr(self.ingester_task, 'task', task_name)
            setattr(self.ingester_task, 'args', json.dumps(id_pass))
            self.ingester_task.save()
        else:
            obj = PeriodicTask(
                name="{}-Task".format(self.name),
                interval=self.schedule,
                task=task_name,
                args=json.dumps(id_pass),
            )
            obj.save()
            self.ingester_task = obj
        super(Config, self).save(*args, **kwargs)  # Call the "real" save() method.
# =====================================================================================================================
# ================================INGESTER DATABASE STRUCTURE==========================================================
# =====================================================================================================================

class global_url(models.Model):
    domain = models.TextField(unique=True)
    url = models.URLField()
