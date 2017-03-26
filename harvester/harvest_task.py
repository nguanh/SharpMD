from .exception import IHarvest_Exception, IHarvest_Disabled
from .IHarvester import IHarvest
from celery.utils.log import get_task_logger
from .models import Config, Schedule
import logging
import sys
import os
import datetime

PROJECT_DIR = os.path.dirname(__file__)


def harvest_task(package, class_name, config_id):
        #load config files
        try:
            config = Config.objects.get(id=config_id)
            print(config.name)
        except Config.DoesNotExist:
            raise IHarvest_Exception("{} is invalid config_id".format(config_id))

        name = config.name
        log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
        log_name = config.name.strip().replace(" ", "_")
        log_file = os.path.join(log_dir, "{}.log").format(log_name)
        # init logger, generate logger for every tasks
        logger = get_task_logger(name)
        logger.setLevel(logging.INFO)
        # create the logging file handler
        fh = logging.FileHandler(log_file)
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
        source = None
        try:
            source = imported_class(config_id)
            if isinstance(source, IHarvest) is False:
                raise ImportError(class_name + " is not an instance of IHarvest")
            print("Init {}".format(name))
            if source.init():
                print("Starting {}".format(name))
                logger.info("Starting Task %s", name)
                result = source.run()
                print("Finished {}".format(name))
                source.cleanup()
                print("Cleanup {}".format(name))
                start_date = config.start_date
                end_date = config.end_date
                max_date = config.schedule.max_date or datetime.date.today()
                interval = config.schedule.time_interval

                days = 1
                if interval == "all":
                    # no data left to read, deactivate this config
                    config.enabled = False
                    logger.info("{} scheduler is finished. Deactivating".format(name))
                elif interval == "month":
                    days = 30
                elif interval == "week":
                    days = 7
                else:
                    days = 1

                # set new start and end dates by shifting the interval for X days
                # end date cannot be in the future so maximum is today
                if start_date is not None:
                    config.start_date = end_date + datetime.timedelta(days=1)
                    config.end_date = min(max_date, config.start_date + datetime.timedelta(days=days))
                    logger.info("Updating dates: {}-{}".format(
                                config.start_date.strftime("%Y-%m-%d"),
                                config.end_date.strftime("%Y-%m-%d")))

                config.save()
                return True
            else:
                logger.error("Initialization of %s failed", name)
                raise IHarvest_Exception()
        except IHarvest_Exception as e:
            logger.critical(e)
            print("Cleanup {}".format(name))

            if source is not None:
                source.cleanup()
            raise
        except IHarvest_Disabled:
            # task is disabled
            print("Skipping Task", name)
            logger.info("Task %s is disabled and skipped", name)
            raise
        except ImportError as e:
            raise IHarvest_Exception(e)
