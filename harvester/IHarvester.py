import configparser

import datetime
from abc import ABC, abstractmethod

from mysqlWrapper.mariadb import MariaDb
from .exception import IHarvest_Exception, IHarvest_Disabled


class IHarvest(ABC):
    HARVESTER_PATH = "configs/harvester.ini"

    def __init__(self, logger, name, config_path=None):
        self.name = name
        self.logger = logger

        # mainly for testing
        if config_path is None:
            config_path = self.HARVESTER_PATH

        # load config
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        if name not in self.config:
            raise IHarvest_Exception("Error: Config could not be loaded")

        # connect to database
        try:
            self.connector = MariaDb(db="harvester")
            self.logger.debug("MariaDB connection successful")
        except Exception as err:
            raise IHarvest_Exception("MARIADB ERROR: {}".format(err))
        # check certain parameters in specific config
        self.configValues = dict(self.config[name])


        #check enabled
        try:
            self.enabled = self.config[name].getboolean("enabled")
            if self.enabled is None:
                raise KeyError()
        except KeyError as e:
            raise IHarvest_Exception("Error: config value {} not found".format(e))

        if self.enabled is False:
            self.connector.close_connection()
            raise IHarvest_Disabled()
        # check optional limit
        if "limit" in self.configValues:
            try:
                self.limit = int(self.configValues["limit"])
                if self.limit < 0:
                    raise Exception()
            except:
                raise IHarvest_Exception("Error: Invalid limit")
        else:
            self.limit = None

        # check dates
        # set start date
        if "start" not in self.configValues or self.configValues["start"] == '':
            # if empty or not defined
            self.start_date = None
        else:
            try:
                self.start_date = datetime.datetime.strptime(self.configValues["start"], "%Y-%m-%d")
            except:
                raise IHarvest_Exception("Error: Invalid Start Date")

        if "end" not in self.configValues or self.configValues["end"] == '':
            self.end_date = None
        else:
            try:
                self.end_date = datetime.datetime.strptime(self.configValues["end"], "%Y-%m-%d")
            except:
                raise IHarvest_Exception("Error: Invalid End Date")

        if( isinstance(self.start_date,datetime.datetime) and isinstance(self.end_date,datetime.date) and
            self.end_date < self.start_date):
            raise IHarvest_Exception("Error: End Date is before Start Date")


    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def run(self):
        pass
