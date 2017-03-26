import configparser

import datetime
from abc import ABC, abstractmethod

from mysqlWrapper.mariadb import MariaDb
from .exception import IHarvest_Exception, IHarvest_Disabled
from .models import Config
import logging


class IHarvest(ABC):
    HARVESTER_PATH = "configs/harvester.ini"

    def __init__(self,config_id):
        # get values from config object
        config = Config.objects.get(id=config_id)
        self.name = config.name
        self.enabled = config.enabled
        self.limit = config.limit
        self.extra = config.extra_config
        self.start_date = config.start_date
        self.end_date = config.end_date
        self.url = config.url
        self.table_name = config.table_name

        self.logger = logging.getLogger(self.name)

        # connect to database
        try:
            self.connector = MariaDb(db="harvester")
            self.logger.debug("MariaDB connection successful")
        except Exception as err:
            raise IHarvest_Exception("MARIADB ERROR: {}".format(err))
        # check certain parameters in specific config

        if self.enabled is False:
            self.connector.close_connection()
            raise IHarvest_Disabled()



    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass
