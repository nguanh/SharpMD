from harvester.IHarvester import IHarvest
from oai.queries import OAI_DATASET
from oai.oaimph_parser import harvestOAI
import datetime


class OaiHarvester(IHarvest):

    def __init__(self, config_id):
        # call constructor of base class for initiating values
        IHarvest.__init__(self, config_id)

    def init(self):
        # create database if not available
        if self.connector.createTable(self.table_name, OAI_DATASET):
            self.logger.info("Table %s created", self.table_name)
            try:
                pass
                #self.connector.execute_ex("CREATE FULLTEXT INDEX title_idx  ON oaipmh_articles (title)", ())
            except:
                self.logger.info("Index already exists")
            return True
        else:
            self.logger.critical("Table could not be created")
            return False

    # time_begin and time_end are always valid datetime objects
    def run(self):
        start = None if self.start_date is None else self.start_date.strftime("%Y-%m-%d")
        end = None if self.end_date is None else self.end_date.strftime("%Y-%m-%d")
        return harvestOAI(self.url, self.connector, self.logger,
                          startDate=start,
                          endDate=end,
                          limit=self.limit)
    def cleanup(self):
        try:
            self.connector.close_connection()
        except:
            pass



