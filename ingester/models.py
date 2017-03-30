from __future__ import absolute_import, unicode_literals
from django.db import models
from django_celery_beat.models import PeriodicTask,IntervalSchedule
from .helper import get_name_block,normalize_title
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

# ======================================= URL =========================================================================
class global_url(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=150)
    url = models.URLField()

class local_url(models.Model):
    global_url = models.ForeignKey(global_url, default=None)
    #auto set date on creation
    last_updated = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=150)


# ======================================= AUTHORS =====================================================================
#Visible on admin interface for editing
class authors_model(models.Model):
    main_name = models.TextField()
    block_name = models.TextField(blank=True)
    website = models.TextField(blank=True, null=True, default=None)
    contact = models.TextField(blank=True, null=True, default=None)
    about = models.TextField(blank=True, null=True, default=None)
    orcid_id = models.CharField(max_length=200,blank=True, null=True, default=None)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.block_name

    def save(self, *args, **kwargs):
        #auto normalize author name
        self.block_name = get_name_block(self.main_name)
        super(authors_model, self).save(*args, **kwargs)


class publication_author(models.Model):
    url = models.ForeignKey(local_url)
    author = models.ForeignKey(authors_model)
    priority = models.IntegerField()


class author_aliases(models.Model):
    alias = models.CharField(max_length=200 )
    author = models.ForeignKey(authors_model)
    class Meta:
        unique_together=('alias','author')

class author_alias_source(models.Model):
    alias = models.ForeignKey(author_aliases)
    url = models.ForeignKey(local_url)
    class Meta:
        unique_together = ("alias","url")

# ======================================= PUBLICATIONS ================================================================


class cluster(models.Model):
    name= models.TextField()
    #TODO zusätzliche indizes für bessere Suche?


class publication(models.Model):
    url = models.ForeignKey(local_url)
    cluster = models.ForeignKey(cluster)
    differences = models.TextField(null=True, default= None)
    title = models.TextField()
    pages = models.CharField(max_length=20, null=True, default=None)
    note = models.TextField(null=True, default=None)
    doi = models.TextField(null=True, default=None)
    abstract = models.TextField(null=True, default=None)
    copyright = models.TextField(null=True, default=None)
    date_added = models.DateField(null=True,default=None)
    date_published = models.DateField(null=True,default=None)
    volume = models.CharField(max_length=20, null=True, default=None)
    number = models.CharField(max_length=20, null=True, default=None)

# ==================================== PUBLICATION MEDIUM =============================================================

class pub_medium(models.Model):
    main_name = models.TextField()
    block_name = models.TextField(blank=True)
    series = models.CharField( max_length=200,blank=True, null=True, default=None)
    edition = models.CharField( max_length=200,blank=True, null=True, default=None)
    location = models.CharField( max_length=200,blank=True, null=True, default=None)
    publisher = models.CharField( max_length=200,blank=True, null=True, default=None)
    institution = models.CharField( max_length=200,blank=True, null=True, default=None)
    school = models.CharField( max_length=200,blank=True, null=True, default=None)
    address = models.CharField( max_length=200,blank=True, null=True, default=None)
    isbn = models.CharField( max_length=200,blank=True, null=True, default=None)
    howpublished = models.CharField( max_length=200,blank=True, null=True, default=None)
    book_title = models.CharField( max_length=200,blank=True, null=True, default=None)
    journal = models.CharField( max_length=200,blank=True, null=True, default=None)

    def __str__(self):
        return self.block_name

    def save(self, *args, **kwargs):
        # auto normalize author name
        self.block_name = normalize_title(self.main_name)
        super(pub_medium, self).save(*args, **kwargs)


class pub_medium_alias(models.Model):
    alias = models.CharField(max_length=200)
    medium = models.ForeignKey(pub_medium)

    class Meta:
        unique_together = ('alias','medium')


class pub_alias_source(models.Model):
    alias = models.ForeignKey(pub_medium_alias)
    url = models.ForeignKey(local_url)

    class Meta:
        unique_together = ("alias", "url")

# ===========================================NON-HARVEST===============================================================
# the values in these tables are not harvested but set by users or admin


class publication_type(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True,default=None)


class study_field(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, default=None)
