from .Iingester import Iingester
from .exception import IIngester_Exception, IIngester_Disabled
from .constants import DATABASE_NAME, CONFIG_PATH
from .ingester import ingest_data2
import configparser
import logging
import sys
import os


def ingest_task(package, class_name, config_path=CONFIG_PATH, **parameters):
        """
        :param package: relative path to package
        :param class_name: class name in package
        :param name: name of the harvester (important for config)
        :param parameters: parameters for harvester as dict parameters
        :return:
        """

        # init logger, generate logger for every tasks
        logger = logging.getLogger("ingester")
        logger.setLevel(logging.DEBUG)
        # create the logging file handler
        fh = logging.FileHandler("{}.log".format("ingester"))
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        logger.addHandler(fh)

        try:
            # add path to system
            file_path = os.path.realpath(__file__)
            project_path = os.path.dirname(os.path.dirname(file_path))
            sys.path.append(project_path)
            # import class from parameters
            mod = __import__(package, fromlist=[class_name])
            imported_class = getattr(mod, class_name)
        except ImportError as e:
            logger.error(e)
            raise

        except AttributeError as e:
            logger.error(e)
            raise

        try:
            source = imported_class(DATABASE_NAME, "harvester", **parameters)
            if isinstance(source, Iingester) is False:
                raise IIngester_Exception(class_name + " is not an instance of IIngest")
            name = source.get_name()
            print("Starting ingestion of ", name)
            # get config
            config = configparser.ConfigParser()
            config.read(config_path)
            config[name].getboolean("enabled")
            # check enable status
            enabled = config[name].getboolean("enabled")
            if enabled is None:
                raise IIngester_Exception("Error %s has no enable status set", name)
            if enabled is False:
                raise IIngester_Disabled()
            config[name].getboolean("enabled")
            # set limit in Iingester
            if "limit" in config[name]:
                limit = int(config[name]["limit"])
                source.set_limit(limit)
            logger.info("Initialize custom ingester %s", name)
            result = ingest_data2(source, DATABASE_NAME)
            print(result)
            logger.info("Included %s", result)
            logger.info("Ingestion finished %s", name)
            return True
        except IIngester_Exception as e:
            logger.critical(e)
            raise
        except IIngester_Disabled:
            # task is disabled
            print("Skipping Task")
            logger.info("Task is disabled and skipped")
            raise
