
from .models import PDFDownloadQueue,SingleReference,OpenReferences
from .exceptions import GrobidException,PDFException
from requests.exceptions import ConnectionError
import requests
import os
import datetime
import logging
from time import sleep
from django.db.models import Q
from lxml import etree
import msgpack

class PdfDownloader:
    namespace = "{http://www.tei-c.org/ns/1.0}"

    def __init__(self, output_folder, grobid_url, logger=None, limit=None):
        self.successful = 0
        self.skipped = 0
        self.invalid = 0
        self.output_folder = output_folder
        if logger is None:
            # empty logger
            self.logger = logging.getLogger()
        else:
            self.logger = logger
        if limit is not None and limit < 1:
            raise PDFException("Invalid limit")
        self.limit = limit
        self.now = datetime.datetime.utcnow()
        self.grobid_url = grobid_url

    def get_result(self):
        return {
            "successful": self.successful,
            "skipped": self.skipped,
            "invalid": self.invalid,
        }

    @staticmethod
    def nameDot(name):
        if len(name) == 1:
            name += "."
        return name

    def parsePersName(self, element):
        lastname = ""
        firstname = ""
        middlename = ""
        if element[0].tag.replace(self.namespace, '') != "persName":
            return None
        for i in element[0]:
            if i.tag.replace(self.namespace, '') == "surname":
                lastname = i.text + " "
            elif i.tag.replace(self.namespace, '') == "forename" and i.get("type") == "first":
                firstname += self.nameDot(i.text) + " "
            elif i.tag.replace(self.namespace, '') == "forename":
                middlename += self.nameDot(i.text) + " "

        finalname = "{} {} {}".format(firstname.strip(), middlename.strip(), lastname.strip())
        # replace double white space with single
        finalname = finalname.replace("  ", " ")
        return finalname

    def parseMonogr(self,element):
        result = {
            "title": None,
            "pubyear": None,
            "authors": []
        }
        for i in element:
            if i.tag.replace(self.namespace, '') == "title":
                result["title"] = i.text

            if i.tag.replace(self.namespace, '') == "imprint":
                for el in i:
                    if el.tag.replace(self.namespace, '') == "date":
                        result["pubyear"] = el.get("when")
            if i.tag.replace(self.namespace, '') == "author":
                result["authors"].append(self.parsePersName(i))

        return result

    @staticmethod
    def get_reference(tei_doc):
        """
        http://teibyexample.org/examples/TBED03v00.htm?target=biblStruct
        if analytic is defined, get title, year and author from it as it represents the smallest unit
        otherwise use monogr
        :param tei_doc:
        :return:
        """
        reference = {}
        monogr = tei_doc["monogr"]
        if "analytic" in tei_doc:
            analytic = tei_doc["analytic"]
            reference["title"] = tei_doc["analytic"]["title"]
            reference["pubyear"] = analytic["pubyear"] or monogr["pubyear"]
            reference["authors"] = analytic["authors"]
        else:
            reference = monogr

        # validate for existing title and authors
        if not len(reference["authors"]) or not reference["title"]:
            return None
        if reference["pubyear"] is not None:
            reference["pubyear"] = datetime.date(int(reference["pubyear"]),1,1)
        return reference

    def parse_references(self, file_path,source):
        if not os.path.isfile(file_path):
            self.logger.error("File {} does not exist".format(file_path))
            return False
        if not file_path.endswith(".pdf"):
            self.logger.error("File {} is not pdf".format(file_path))
            return False
        try:
            requests.post(self.grobid_url)
        except ConnectionError:
            raise GrobidException("Grobid does not answer")

        # file and connection are OK

        with open(file_path, "rb") as f:
            ref_handler = requests.post(self.grobid_url, files={"input": f})
        if ref_handler.ok is False:
            self.logger.error("File {} error {} when sending to Grobid".format(file_path,ref_handler.status_code))
            return False
        parser2 = etree.XMLPullParser(tag="{}biblStruct".format(self.namespace), load_dtd=True)
        parser2.feed(ref_handler.text)
        result = {}
        for action, elem in parser2.read_events():
            for i in elem:

                if i.tag.replace(self.namespace, '') == "monogr":
                    result["monogr"] = self.parseMonogr(i)
                if i.tag.replace(self.namespace, '') == "analytic":
                    result["analytic"] = self.parseMonogr(i)
            reference = self.get_reference(result)
            self.logger.debug("Original : %s", result)
            self.logger.debug("Reference: %s", reference)
            if reference is None:
                self.logger.debug("Invalid reference")
            else:
                author_list = msgpack.packb(";".join(reference["authors"]))
                SingleReference.objects.create(source=source,
                                               title= reference["title"],
                                               authors=author_list,
                                               date = reference["pubyear"])

            # TODO write single reference

    def process_pdf(self):
        while True:
            # get first entry in downloadqueue
            url_object = PDFDownloadQueue.objects.filter(Q(last_try__lt=self.now) | Q(last_try=None)).first()
            if url_object is None:
                return self.get_result()
            # backup values and pop entry
            url_dict = {
                "url": url_object.url,
                "tries": url_object.tries,
                "lasttry": url_object.last_try,
                "source": url_object.source
            }
            url_object.delete()
            filename = url_dict["url"].split("/")[-1]
            output = os.path.join(self.output_folder, filename)
            if os.path.isfile(output) is True:
                self.logger.warning("{} already exists".format(filename))
                self.skipped += 1

            # TODO alternating header and cookies
            file_request = requests.get(url_dict["url"])
            if file_request.status_code == 404:
                # file does not exist, keep it deleted
                self.logger.error("Error: file not found {}".format(filename))
                self.invalid += 1
                continue
            elif file_request.status_code == 403:
                # crawl blocked, wait for later
                self.logger.warning("{} access was blocked, adding to queue".format(filename))
                PDFDownloadQueue.objects.create(url=url_dict["url"],
                                                tries=url_dict["tries"] + 1,
                                                last_try=self.now,
                                                source=url_dict["source"])
                self.skipped += 1
                continue
            elif file_request.ok is False:
                self.logger.error("Error: {}".format(file_request.status_code))
                PDFDownloadQueue.objects.create(url=url_dict["url"],
                                                tries=url_dict["tries"] + 1,
                                                last_try=self.now,
                                                source=url_dict["source"])
                continue

            with open(output, "wb") as f:
                f.write(file_request.content)
                self.logger.info("{} download success".format(filename))
                self.successful += 1

            self.logger.info("Waiting...")
            sleep(8)
            # add grobid
            if not self.parse_references(output):
                pass
            self.logger.info("Continuing")
            if self.limit is not None:
                self.limit -= 1
            if self.limit == 0:
                return self.get_result()


def download_queue(output_folder, logger=None, limit=None):
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
