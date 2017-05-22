from harvester.IHarvester import IHarvest
from .queries import DBLP_ARTICLE
from harvester.exception import IHarvest_Exception
from .xml_parser import parse_xml
from fileDownloader.fileDownloader import download_file
import urllib.parse
import subprocess
import os
import datetime


class DblpHarvester(IHarvest):
    """
    Harvester Sub Component for DBLP
    xml_url: url to dblp xml file
    dtd_url: url to dblp dtd file
    extraction_path: folder where downloaded data is stored
    tags: publication types to be included (for example: article, phdthesis)
    """
    def __init__(self, config_id):
        # call constructor of base class for initiating values
        IHarvest.__init__(self, config_id)
        try:
            # check paths for all dblp files, and paths for storing the files
            # get values from extra parameters, parsed by IHarvest
            self.tags = self.extra["tags"]
            # file download requirements
            self.xml_url = urllib.parse.urljoin(self.url, self.extra["zip_name"])
            self.dtd_url = urllib.parse.urljoin(self.url, self.extra["dtd_name"])

            if os.path.isdir(self.extra["extraction_path"]) is False:
                raise IHarvest_Exception("Invalid DBLP extraction path")
            self.extraction_path = self.extra["extraction_path"]
            self.xml_path = os.path.join(self.extraction_path, self.extra["xml_name"])
            self.dtd_path = os.path.join(self.extraction_path, self.extra["dtd_name"])
        except KeyError as e:
            self.logger.critical("Config value %s missing", e)
            raise IHarvest_Exception("Error: config value {} not found".format(e))

        # convert tags to tuple
        if isinstance(self.tags, list):
            self.tags = tuple(self.tags)
        else:
            raise IHarvest_Exception("Invalid Tags")

    def init(self):
        """
        Init harvester by downloading files, extracting xml file from .gz
        creating harvester table, if non existent
        :return:
        """
        if self.connector.createTable(self.table_name, DBLP_ARTICLE):
            self.logger.info("Table %s created", self.table_name)
            # create temporary index
            self.connector.execute_ex("CREATE FULLTEXT INDEX title_idx  ON dblp_article (title)", ())
        else:
            self.logger.critical("Table could not be created")
            return False
        # download files
        try:
            xml_result = download_file(self.xml_url, self.extraction_path)
            dtd_result = download_file(self.dtd_url, self.extraction_path)
        except:
            self.logger.critical("files could not be downloaded")
            return False
        if xml_result and dtd_result:
            self.logger.info("Files were created")
            self.logger.info("Extracting .gz file")
            # use unix tool for extraction
            result = subprocess.call(["gunzip", xml_result])
            if result == 0:
                self.logger.info("Files were extracted")
                return True
        self.logger.critical("Unknown Error")
        return False

    # time_begin and time_end are always valid datetime objects
    def run(self):
        """
        parse downloaded xml file and include all datasets containing:
        1. the matching tag
        2. mdate is between start and enddate
        :return:
        """
        start = None if self.start_date is None else datetime.datetime.combine(self.start_date, datetime.time.min)
        end = None if self.end_date is None else datetime.datetime.combine(self.end_date, datetime.time.min)
        return parse_xml(self.xml_path, self.dtd_path, self.connector, self.logger,
                         self.tags, start, end, self.limit)

    def cleanup(self):
        """
        remove downloaded files
        close mysql connector
        :return:
        """
        if os.path.isfile(self.xml_path):
            os.remove(self.xml_path)
            self.logger.info("Xml files removed")

        if os.path.isfile(self.dtd_path):
            os.remove(self.dtd_path)
            self.logger.info("DTD files removed")
        #try to close mysql connection if not already closed
        try:
            self.connector.close_connection()
        except:
            pass




