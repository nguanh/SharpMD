from django.db import models

# Create your models here.


class PDFDownloadQueue(models.Model):
    # url to pdf
    url = models.URLField()
    # unsuccessful tries
    tries = models.IntegerField(default=0)
    # last unsuccessful attempt
    last_try = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.url


