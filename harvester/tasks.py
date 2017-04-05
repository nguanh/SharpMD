# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.exceptions import Ignore
from celery import states
from .exception import IHarvest_Disabled,IHarvest_Exception
from .harvest_task import harvest_task
from .models import Config
from SharpMD.celery import app



@shared_task
def test(package,class_name,config_id):
    try:
        config = Config.objects.get(id= config_id)
        print(config.name)
    except Config.DoesNotExist:
        print("config not found")



@shared_task
def harvestsource(package, class_name, config_id):
    print("Active:",len(app.control.inspect().active()))
    print("Reserved:",len(app.control.inspect().reserved()))
    """

    :param package: relative path to package
    :param class_name: class name in package
    :param config_id: id of config model containing all config related data
    :return:
    """
    try:
        harvest_task(package, class_name, config_id)
    except ImportError as e:
        harvestsource.update_state(
            state=states.FAILURE,
            meta=e,
        )
        raise Ignore()
    except IHarvest_Exception as e:
        harvestsource.update_state(
            state=states.FAILURE,
            meta=e
        )
    except IHarvest_Disabled:
        # task is disabled
        harvestsource.update_state(
            state=states.SUCCESS,
            meta=''
        )
