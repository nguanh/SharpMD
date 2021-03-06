from django.db import models
from ingester.models import local_url
import msgpack
# Create your models here.
STATUS_CHOICES = (
    ('OP', 'OPEN'),
    ('INC', 'INCOMPLETE'),
    ('LIM', 'LIMBO'),
    ('FIN', 'FINISHED'),
)


class OpenReferences(models.Model):
    # harvester table
    source_table = models.IntegerField()
    # key in harvester table
    source_key = models.CharField(max_length=150, db_index=True)
    # ingester local url id
    ingester_key = models.ForeignKey(local_url, null=True, default=None)
    last_updated = models.DateField(auto_now=True)

    def __str__(self):
        return "{}-{}".format(self.source_table, self.source_key)

    def test(self):
        return [self.source_table, self.source_key,None]


class SingleReference(models.Model):
    source = models.ForeignKey(OpenReferences)
    title = models.TextField()
    date = models.DateField(default= None, null=True)
    # authors are serialized
    authors = models.BinaryField()
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='OP')
    tries = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def test(self):
        authors = msgpack.unpackb(self.authors, encoding="utf-8")
        return [self.source.id, self.title, self.date, authors, self.status]


class PDFDownloadQueue(models.Model):
    # url to pdf
    url = models.URLField()
    # unsuccessful tries
    tries = models.IntegerField(default=0)
    # last unsuccessful attempt
    last_try = models.DateTimeField(blank=True, null=True, default=None)
    source = models.ForeignKey(OpenReferences, null=True)

    class Meta:
        unique_together = ('url', 'source')

    def __str__(self):
        return self.url

    def test(self):
        return [self.url, self.tries,self.source.id]






