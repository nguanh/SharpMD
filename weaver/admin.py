from django.contrib import admin
from .models import *
from .PDFDownloader import *
from .Referencer import *
# Register your models here.
import logging
from conf.config import get_config


PROJECT_DIR = os.path.dirname(__file__)
log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")

def start_referencing(modeladmin,request,queryset):
    logger = logging.getLogger("Referencer")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    log_file = os.path.join(log_dir, "pdf_downloader.log")
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    logger.info("Start Referencer")

    ref = Referencer(limit=3000, logger=logger)
    ref.run(test_mode=True)



class ReferenceAdmin(admin.ModelAdmin):
    actions = [start_referencing]
admin.site.register(PDFDownloadQueue)
admin.site.register(SingleReference, ReferenceAdmin)
