from __future__ import absolute_import, unicode_literals
from celery import shared_task
from conf.config import get_config
from .PDFDownloader import PdfDownloader
from .Referencer import Referencer
from SharpMD.celery import app
import os
import logging
PROJECT_DIR = os.path.dirname(__file__)
log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")


@shared_task
def pdfdownloader(limit = None):
    """
    task for downloading pdf files, sending them to grobid and create single references
    :return:
    """
    # check if task is already running
    parameter_list = "[]"
    matches = 0
    active_queue = app.control.inspect().active()["celery@bremen"]
    for active_task in active_queue:
        if active_task["args"] == parameter_list:
            matches += 1
    if matches > 1:
        print("PDF Downloader Task is already running, skipping execution")
        return None

    # create logger
    logger = logging.getLogger("PDFDownloader")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    log_file = os.path.join(log_dir, "pdf_downloader.log")
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    # run actual task
    tmp = get_config("FOLDERS")["tmp"]
    grobid = get_config("WEAVER")["grobid"]
    if limit is None:
        limit = int(get_config("WEAVER")["pdf_limit"])

    logger.info("Init PDF Processing")
    obj = PdfDownloader(tmp, grobid, logger=logger, limit=limit)
    logger.info("Start Processing")
    result = obj.process_pdf()
    logger.info(result)


@shared_task
def referencertask(limit=None):
    parameter_list = "[]"
    matches = 0
    active_queue = app.control.inspect().active()["celery@bremen"]
    for active_task in active_queue:
        if active_task["args"] == parameter_list:
            matches += 1
    if matches > 1:
        print("Referencer Task is already running, skipping execution")
        return None

    # create logger
    logger = logging.getLogger("Referencer")
    logger.setLevel(logging.INFO)
    # create the logging file handler
    log_file = os.path.join(log_dir, "referencer.log")
    fh = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add handler to logger object
    logger.addHandler(fh)
    logger.info("Start Referencer")


    if limit is None:
        limit = int(get_config("WEAVER")["referencer_limit"])

    ref = Referencer(limit, logger=logger)
    ref.run()
    logger.info("Finished Referencer")


