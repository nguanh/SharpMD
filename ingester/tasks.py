# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.exceptions import Ignore
from celery import states
from .exception import IIngester_Exception,IIngester_Disabled
#from .ingest_task import ingest_task
from .constants import CONFIG_PATH


@shared_task
def ingestsource(package, class_name):
    try:
        pass
        #ingest_task(package, class_name, config_path=CONFIG_PATH)
    except ImportError as e:
        ingestsource.update_state(
            state=states.FAILURE,
            meta=e,
        )
        raise Ignore()
    except IIngester_Exception as e:
        ingestsource.update_state(
            state=states.FAILURE,
            meta=e
        )
    except IIngester_Disabled:
        # task is disabled
        ingestsource.update_state(
            state=states.SUCCESS,
            meta=''
        )