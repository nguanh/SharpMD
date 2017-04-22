# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.exceptions import Ignore
from celery import states
from .exception import IIngester_Exception,IIngester_Disabled
from .ingest_task import ingest_task
from SharpMD.celery import app


@shared_task
def ingestsource(package, class_name,config_id):
    # Check if task is already running by checking queue for task with same parameters
    active_queue = app.control.inspect().active()["celery@bremen"]
    # transform parameter to string list for comparision
    parameter_list = "['{}', '{}', {}]".format(package, class_name, config_id)
    matches = 0
    for active_task in active_queue:
        if active_task["args"] == parameter_list:
            matches += 1

    if matches > 1:
        print("Task {} is already running, skipping execution".format(parameter_list))
        return None

    try:
        ingest_task(package, class_name, config_id)

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

