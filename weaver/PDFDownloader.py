
from weaver.models import PDFDownloadQueue
import requests
import os
import datetime
import logging
from time import sleep
from django.db.models import Q

class PDFException(Exception):
    pass


def download_queue(output_folder, logger=None, limit= None):
    successful = 0
    skipped = 0
    invalid = 0
    if logger is None:
        # empty logger
        logger = logging.getLogger()
    if limit is not None and limit <1:
        raise PDFException("Invalid limit")

    now = datetime.datetime.utcnow()
    while True:
        # get first entry in downloadqueue
        url_object = PDFDownloadQueue.objects.filter(Q(last_try__lt=now) | Q(last_try=None)).first()
        if url_object is None:
            return {
                "successful": successful,
                "skipped": skipped,
                "invalid": invalid,
            }
        url_dict = {
            "url": url_object.url,
            "tries": url_object.tries,
            "lasttry": url_object.last_try
        }
        url_object.delete()
        filename = url_dict["url"].split("/")[-1]
        output = os.path.join(output_folder, filename)
        if os.path.isfile(output) is True:
            logger.warning("{} already exists".format(filename))
            url_object.delete()
            skipped += 1

        #TODO alternating header and cookies
        file_request = requests.get(url_dict["url"])
        if file_request.status_code == 404:
            logger.error("Error: file not found {}".format(filename))
            invalid += 1
            continue
        elif file_request.status_code == 403:
            # crawl blocked, wait for later
            logger.warning("{} access was blocked, adding to queue".format(filename))
            PDFDownloadQueue.objects.create(url=url_dict["url"],
                                            tries=url_dict["tries"]+1,
                                            last_try=now)
            skipped += 1
            continue
        elif file_request.ok is False:
            logger.error("Error: {}".format(file_request.status_code))
            continue

        with open(output, "wb") as f:
            f.write(file_request.content)
            logger.info("{} download success".format(filename))
            successful += 1
        logger.info("Waiting...")
        sleep(10)
        logger.info("Continuing")
        if limit is not None:
            limit -= 1
        if limit == 0:
            return {
                "successful": successful,
                "skipped": skipped,
                "invalid": invalid,
            }
