from abc import ABC, abstractmethod

from mysqlWrapper.mariadb import MariaDb
from .exception import IHarvest_Exception, IHarvest_Disabled
from .models import Config
import logging
from conf.config import get_config


class IHarvest(ABC):
    """
    Interface for Harvester Sub-Components
    """

    def __init__(self, config_id):
        """

        :param config_id: id of config, see harvester models
        """
        # get values from config object
        config = Config.objects.get(id=config_id)
        # name of sub component
        self.name = config.name
        # is enabled
        self.enabled = config.enabled
        # maximum amount of datasets harvested per execution ( testing purposes)
        self.limit = config.limit
        # additional parameters are passed as a dict
        self.extra = config.extra_config
        # if defined all datasets between start and end date are harvested
        self.start_date = config.start_date
        self.end_date = config.end_date
        # url of source
        self.url = config.url
        # table name of where harvester stores its data
        self.table_name = config.table_name

        if self.limit == 0:
            self.limit = None
        # get logger from name
        self.logger = logging.getLogger("ingester.{}".format(self.name))

        # connect to database
        try:
            # read database from config
            db = get_config("DATABASES")["harvester"]
            self.connector = MariaDb(db=db)
            self.logger.debug("MariaDB connection successful")
        except Exception as err:
            raise IHarvest_Exception("MARIADB ERROR: {}".format(err))

        # check certain parameters in specific config
        if self.enabled is False:
            self.connector.close_connection()
            raise IHarvest_Disabled()

    @abstractmethod
    def init(self):
        """
        method to be called on initialisation
        :return:
        """
        pass

    @abstractmethod
    def run(self):
        """
        method to be called for start harvesting
        :return:
        """
        pass

    @abstractmethod
    def cleanup(self):
        """
        optional method to be called for removing data and cleaning up
        :return:
        """
        pass
