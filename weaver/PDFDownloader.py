
from weaver.models import PDFDownloadQueue
import requests
import os

import logging
from time import sleep



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


    while True:
        # get first entry in downloadqueue
        url_object = PDFDownloadQueue.objects.first()
        if url_object is None:
            return {
                "successful": successful,
                "skipped": skipped,
                "invalid": invalid,
            }
        filename = url_object.url.split("/")[-1]
        output = os.path.join(output_folder, filename)
        if os.path.isfile(output) is True:
            logger.warning("{} already exists".format(filename))
            url_object.delete()
            skipped+=1

        #TODO alternating header and cookies
        file_request = requests.get(url_object.url)
        if file_request.ok is False:
            logging.error("Error: {}".format(file_request.status_code))
            continue

        with open(output, "wb") as f:
            f.write(file_request.content)
            logger.info("{} download success".format(filename))
            successful+=1
        logger.info("Waiting...")
        sleep(10)
        logging.info("Continuing")
        url_object.delete()
        if limit is not None:
            limit -= 1

        if limit == 0:
            return {
                "successful": successful,
                "skipped": skipped,
                "invalid": invalid,
            }
