from harvester.IHarvester import IHarvest
from .queries import DBLP_ARTICLE
from harvester.exception import IHarvest_Exception
from .xml_parser import parse_xml
from fileDownloader.fileDownloader import download_file
import subprocess


class DblpHarvester(IHarvest):
    def __init__(self, logger, name, path=None):
        # call constructor of base class for initiating values
        IHarvest.__init__(self, logger, name, path)

        # get config values
        # required values
        try:
            self.xml_path = self.configValues["xml_path"]
            self.dtd_path = self.configValues["dtd_path"]
            self.tags = self.configValues["tags"]
            self.table_name = self.configValues["table_name"]
            # file download requirements
            self.xml_url = self.configValues["xml_url"]
            self.dtd_url = self.configValues["dtd_url"]
            self.extraction_path = self.configValues["extraction_path"]
        except KeyError as e:
            self.logger.critical("Config value %s missing", e)
            raise IHarvest_Exception("Error: config value {} not found".format(e))

        # convert tags to tuple
        self.tags = tuple(self.tags.split(","))

    def init(self):
        if self.connector.createTable(self.table_name, DBLP_ARTICLE):
            self.logger.info("Table %s created", self.table_name)
        else:
            self.logger.critical("Table could not be created")
            return False
        # download files
        try:
            xml_result = download_file(self.xml_url,self.extraction_path)
            dtd_result = download_file(self.dtd_url,self.extraction_path)
        except:
            self.logger.critical("files could not be downloaded")
            return False
        if xml_result and dtd_result:
            self.logger.info("Files were created")
            result = subprocess.call(["gunzip", xml_result])
            if result == 0:
                self.logger.info("Files were extracted")
                return True
        self.logger.critical("Unknown Error")
        return False

    # time_begin and time_end are always valid datetime objects
    def run(self):
        return parse_xml(self.xml_path, self.dtd_path, self.connector, self.logger,
                         self.tags, self.start_date, self.end_date, self.limit)




