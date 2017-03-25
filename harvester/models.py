from django.db import models
from django_celery_beat.models import IntervalSchedule,PeriodicTask
import os
from django.utils.translation import ugettext_lazy as _
import json

# Create your models here.
#TODO überlegen, wie das ganze als DBLP harvester benutzt werden kann

'''
Mit der Erstellung der Config, soll
- Config gibt den Pfad des Harvester Moduls an
- Config muss überprüfen, ob dieses Modul überhaupt Existiert und eine unterklasse von Iharvest ist
- Task angelegt werden
- Es soll ein ConfigLogger Modell erstellt werden
- Der Configlogger soll einfach nur den Log der Config darstellen
- Dazu liest es die Log Datei ein und stellt sie dar
- Zusätzliche Felder: Crontab (wie häufig) und task name
https://github.com/celery/django-celery-beat
'''

class Schedule(models.Model):
    """
    Schedule determines the way the harvester works.
    The harvester will be executed at times specified in the schedule.
    It will harvest all publications defined in the range of min and max date
    If both are empty, the harvester will harvest all data on every execution

    """
    # total date range of Harvester can both be empty
    name= models.CharField(max_length=200, default=None)
    min_date = models.DateField('Min Date', blank=True, null=True)
    max_date = models.DateField('Max Date', blank=True, null=True)
    schedule = models.ForeignKey(IntervalSchedule, default=None)

    def __str__(self):
        return self.name


class Config(models.Model):
    # Name of the harvester for identification
    # name of harvester for logger
    name = models.CharField(max_length=200)
    # table used by harvester
    table_name = models.CharField(max_length=200)
    #start and end date for selective harvesting, set implicitly by selecting a schedule
    start_date = models.DateField('Start Date', blank=True, null=True, editable=False)
    end_date = models.DateField('End Date',blank=True, null=True, editable=False)
    # amount of publications added per harvest
    limit = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)
    # source url
    url = models.URLField()
    # addition config parameters set as json
    extra_config = models.TextField(blank=True, default='{}')
    # extra parameter  for tasks
    task_parameter= models.TextField(blank=True, default='{}')

    # task is not visible on creation
    schedule = models.ForeignKey(Schedule, default=None)
    task = models.CharField(_('task name'), max_length=200)
    celery_task = models.ForeignKey(PeriodicTask,default=None, null=True, blank=True)

    def __str__(self):
        return self.name

    # wird aufgerufen, sobald ein neuer Harvester erstellt wird, oder verändert wird
    def save(self, *args, **kwargs):
        #create django celery beat periodic task
        self.celery_task= PeriodicTask(
            name="{}-Task".format(self.name),
            interval=self.schedule.schedule,
            task=self.task,
            args=json.dumps(self.task_parameter),
        )
        self.celery_task.save()
        # self.task = PeriodicTask()

       # schedule, created = IntervalSchedule.objects.get_or_create(every = 10,period = IntervalSchedule.SECONDS)
        #self.task = schedule
        super(Config, self).save(*args, **kwargs) # Call the "real" save() method.



