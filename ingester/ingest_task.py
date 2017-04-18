from .Iingester import Iingester
from .exception import IIngester_Exception, IIngester_Disabled
from conf.config import get_config
from .ingesting_function import ingest_data
from .models import Config
import logging
import sys
import os
import random
PROJECT_DIR = os.path.dirname(__file__)



def test_bug(package,class_name,config_id):
    # init logger, generate logger for every tasks
    logger = logging.getLogger("ingester")
    if not logger.handlers:
        log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
        log_file = os.path.join(log_dir, "TEST.log")
        logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        logger.addHandler(fh)

    logger.info("STARTED")
    logger.info(random.randint(0, 100))


def ingest_task(package, class_name, config_id):
        """
        :param package: relative path to package
        :param class_name: class name in package
        :param config_id: id of config used for this ingester
        :return:
        """
        # ---------------------------------------LOAD CONFIG FROM DB----------------------------------------------------
        try:
            config = Config.objects.get(id=config_id)
            print(config.name)
        except Config.DoesNotExist:
            raise IIngester_Exception("{} is invalid config_id".format(config_id))
        # ------------------------------------- INIT LOGGER-------------------------------------------------------------
        name = config.name
        log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
        log_name = config.name.strip().replace(" ", "_")
        log_file = os.path.join(log_dir, "ingester.{}.log").format(log_name)
        # init logger, generate logger for every tasks
        logger = logging.getLogger("ingester")

        logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        # add handler to logger object
        logger.addHandler(fh)

        # ---------------------------------------LOAD MODULE----------------------------------------------------------
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
            source = imported_class(name)
            if isinstance(source, Iingester) is False:
                raise IIngester_Exception(class_name + " is not an instance of IIngest")
            print("Starting ingestion of ", name)
            # check enable status
            if config.enabled is False:
                raise IIngester_Disabled()
            # set limit in Iingester
            source.set_limit(config.limit)
            logger.info("Initialize custom ingester %s", name)
            result = ingest_data(source)
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
