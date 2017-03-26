from django.db import models
from django_celery_beat.models import IntervalSchedule, PeriodicTask
from django.utils.translation import ugettext_lazy as _
import json
import jsonfield


class Schedule(models.Model):
    """
    Schedule determines the way the harvester works.
    The harvester will be executed at times specified in the schedule.
    It will harvest all publications defined in the range of min and max date
    If both are empty, the harvester will harvest all data on every execution

    """

    INTERVAL_CHOICES = (
        ("all", "All Data"),
        ("month", "Monthly"),
        ("week", "Weekly"),
        ("day", "Daily"),
    )
    # total date range of Harvester can both be empty
    name= models.CharField(max_length=200, default=None)
    min_date = models.DateField('Min Date', blank=True, null=True, default=None)
    max_date = models.DateField('Max Date', blank=True, null=True, default= None)
    schedule = models.ForeignKey(IntervalSchedule, default=None)
    time_interval = models.CharField(max_length=200, default="all", null=True, choices=INTERVAL_CHOICES)

    def __str__(self):
        return self.name


class Config(models.Model):
    # Name of the harvester for identification
    # name of harvester for logger
    name = models.CharField(max_length=200, unique=True)
    # table used by harvester
    table_name = models.CharField(max_length=200)
    # start and end date for selective harvesting, set implicitly by selecting a schedule
    start_date = models.DateField('Start Date', blank=True, null=True, editable=False)
    end_date = models.DateField('End Date', blank=True, null=True, editable=False)
    # amount of publications added per harvest
    limit = models.IntegerField(default=None)
    enabled = models.BooleanField(default=True)
    # source url
    url = models.URLField()
    # addition config parameters set as json
    extra_config = jsonfield.JSONField()
    module_path = models.CharField(max_length=200, default=None)
    module_name = models.CharField(max_length=200, default=None)
    # task is not visible on creation
    schedule = models.ForeignKey(Schedule, default=None)
    task = models.CharField(_('task name'), max_length=200)
    celery_task = models.ForeignKey(PeriodicTask, default=None, null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    # wird aufgerufen, sobald ein neuer Harvester erstellt wird, oder verändert wird
    def save(self, *args, **kwargs):
        # save object to get its id
        # pass config id as third task parameter
        if self.id is None:
            super(Config, self).save(*args, **kwargs)  # Call the "real" save() method.

        print(self.schedule.time_interval)
        # join module path,name and id
        task_args = [self.module_path, self.module_name, self.id]
        if self.celery_task is not None:
            setattr(self.celery_task, 'name', "{}-Task".format(self.name))
            setattr(self.celery_task, 'interval', self.schedule.schedule)
            setattr(self.celery_task, 'task', self.task)
            setattr(self.celery_task, 'args', json.dumps(task_args))
            self.celery_task.save()
        else:
            obj = PeriodicTask(
                name="{}-Task".format(self.name),
                interval=self.schedule.schedule,
                task=self.task,
                args=json.dumps(task_args),
            )
            obj.save()
            self.celery_task = obj
        super(Config, self).save(*args, **kwargs)  # Call the "real" save() method.



