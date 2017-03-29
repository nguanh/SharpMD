from .oaiharvester import OaiHarvester
from .queries import ARXIV_ARTICLE, ADD_ARXIV
from .oaimph_parser import harvestOAI
from .arxiv_handler import ArXivRecord, parse_arxiv
import datetime


class ArXivHarvester(OaiHarvester):

    def __init__(self, config_id):
        # call constructor of base class for initiating values
        OaiHarvester.__init__(self, config_id)

    def init(self):
        # create database if not available
        if self.connector.createTable(self.table_name, ARXIV_ARTICLE):
            self.logger.info("Table %s created", self.table_name)
            return True
        else:
            self.logger.critical("Table could not be created")
            return False

    # time_begin and time_end are always valid datetime objects
    def run(self):
        start = None if self.start_date is None else self.start_date.strftime("%Y-%m-%d")
        end = None if self.end_date is None else self.end_date.strftime("%Y-%m-%d")
        return harvestOAI(self.url, self.connector, self.logger,
                          processing_function=parse_arxiv, xml_format="arXiv",
                          query=ADD_ARXIV, parsing_class=ArXivRecord,
                          startDate=start,
                          endDate=end,
                          limit=self.limit)


