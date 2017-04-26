from __future__ import absolute_import, unicode_literals
from django.db import models
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from .helper import get_name_block, normalize_title,normalize_authors
import json
from django.db.models.signals import pre_delete

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



    def __str__(self):
        return self.name

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

class keywordsModel(models.Model):
    main_name = models.TextField()
    block_name = models.TextField(blank=True)
    description = models.TextField(blank=True, null=True, default=None)

    def __str__(self):
        return self.block_name

    def save(self, *args, **kwargs):
        # auto normalize author name
        self.block_name = normalize_title(self.main_name)
        super(keywordsModel, self).save(*args, **kwargs)

    def test(self):
        return [self.main_name, self.block_name]


# ===========================================NON-HARVEST===============================================================
# the values in these tables are not harvested but set by users or admin


class publication_type(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True,null=True,default=None)


class study_field(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True, default=None)

# ======================================= URL =========================================================================
class global_url(models.Model):
    id = models.AutoField(primary_key=True)
    domain = models.CharField(max_length=150)
    url = models.URLField()

class local_url(models.Model):
    global_url = models.ForeignKey(global_url, default=None)
    #auto set date on creation
    last_updated = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=150, db_index=True)
    medium = models.ForeignKey(pub_medium, default=None, null=True, blank=True)
    type = models.ForeignKey(publication_type, default=None, null=True, blank=True)
    study_field = models.ForeignKey(study_field, default=None,null=True,blank=True)
    def test(self):
        medium = None if self.medium is None else self.medium.id
        u_type = None if self.type is None else self.type.id
        sf = None if self.study_field is None else self.study_field.id
        return [self.global_url.id, self.url, medium, u_type, sf]


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
        self.block_name = normalize_authors(self.main_name)
        super(authors_model, self).save(*args, **kwargs)

    def test(self):
        return [self.main_name,self.block_name]


class publication_author(models.Model):
    url = models.ForeignKey(local_url)
    author = models.ForeignKey(authors_model)
    priority = models.IntegerField()

    def test(self):
        return[self.url.id, self.author.id,self.priority]

    class Meta:
        unique_together=('url','author')


class author_aliases(models.Model):
    alias = models.CharField(max_length=200, db_index=True)
    author = models.ForeignKey(authors_model)

    def test(self):
        return [self.author.id,self.alias]

    def __str__(self):
        return self.alias

    class Meta:
        unique_together=('alias','author')
        #index_together=('alias','author')





class author_alias_source(models.Model):
    alias = models.ForeignKey(author_aliases)
    url = models.ForeignKey(local_url)

    def test(self):
        return [self.alias.id,self.url.id]

    class Meta:
        unique_together = ("alias","url")

# ======================================= PUBLICATIONS ================================================================


class cluster(models.Model):
    name= models.TextField()


class publication(models.Model):
    url = models.ForeignKey(local_url)
    cluster = models.ForeignKey(cluster)
    differences = models.BinaryField(null=True, default= None)
    title = models.TextField()
    pages = models.CharField(max_length=20, null=True, default=None)
    note = models.TextField(null=True, default=None)
    doi = models.TextField(null=True, default=None)
    abstract = models.TextField(null=True, default=None)
    copyright = models.TextField(null=True, default=None)
    date_added = models.DateField(null=True, default=None)
    date_published = models.DateField(null=True, default=None)
    volume = models.CharField(max_length=20, null=True, default=None)
    number = models.CharField(max_length=20, null=True, default=None)

    def test(self):
        return [self.url.id, self.cluster.id, self.title]


# ==================================== PUBLICATION MEDIUM =============================================================


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

# =============================================== KEYWORDS ===============================================================


class publication_keyword(models.Model):
    url = models.ForeignKey(local_url)
    keyword = models.ForeignKey(keywordsModel)

    def test(self):
        return [self.url.id, self.keyword.id]

    class Meta:
        unique_together = ('url', 'keyword')


class keyword_aliases(models.Model):
    alias = models.CharField(max_length=200)
    keyword = models.ForeignKey(keywordsModel)

    def test(self):
        return [self.keyword.id, self.alias]

    class Meta:
        unique_together = ('alias', 'keyword')


class keyword_alias_source(models.Model):
    alias = models.ForeignKey(keyword_aliases)
    url = models.ForeignKey(local_url)

    def test(self):
        return [self.alias.id, self.url.id]

    class Meta:
        unique_together = ("alias", "url")


# =============================================== LIMBO ===============================================================

class limbo_pub(models.Model):
    reason = models.CharField(max_length=100)
    url = models.CharField(max_length=150)
    title = models.TextField()
    pages = models.CharField(max_length=20, default=None, null=True)
    note = models.TextField(default=None, null=True)
    doi = models.CharField(max_length=200, default=None, null=True)
    abstract = models.TextField(default=None, null=True)
    copyright = models.TextField(default=None, null=True)
    date_added = models.DateField(null=True,default=None)
    date_published = models.DateField(null=True,default=None)
    volume = models.CharField(max_length=20, null=True, default=None)
    number = models.CharField(max_length=20, null=True, default=None)
    series = models.CharField(max_length=200, blank=True, null=True, default=None)
    edition = models.CharField(max_length=200, blank=True, null=True, default=None)
    location = models.CharField(max_length=200, blank=True, null=True, default=None)
    publisher = models.CharField(max_length=200, blank=True, null=True, default=None)
    institution = models.CharField(max_length=200, blank=True, null=True, default=None)
    school = models.CharField(max_length=200, blank=True, null=True, default=None)
    address = models.CharField(max_length=200, blank=True, null=True, default=None)
    isbn = models.CharField(max_length=200, blank=True, null=True, default=None)
    howpublished = models.CharField(max_length=200, blank=True, null=True, default=None)
    book_title = models.CharField(max_length=200, blank=True, null=True, default=None)
    journal = models.CharField(max_length=200, blank=True, null=True, default=None)

    def test_extended(self):
        return [self.reason,self.url, self.title,self.pages,self.note,self.doi,self.abstract,self.copyright,
         self.date_added,self.date_published,self.volume,self.number,self.series,self.edition,self.publisher,
         self.institution,self.school,self.address,self.isbn,self.howpublished,self.book_title,self.journal]


class limbo_authors(models.Model):
    publication = models.ForeignKey(limbo_pub)
    reason = models.CharField(max_length=100)
    name = models.TextField()
    priority = models.IntegerField(null=True, default=None)

    def test(self):
        return [self.publication.id, self.reason, self.name, self.priority]


def delete_task(sender, instance, using, **kwargs):
    try:
        instance.ingester_task.delete()
    except Exception as e:
        print(e)

pre_delete.connect(delete_task, sender=Config)