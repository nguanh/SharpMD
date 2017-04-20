from django.shortcuts import render
from django.shortcuts import get_object_or_404
import os
import tailer
from .models import Config
PROJECT_DIR = os.path.dirname(__file__)


def log(request, config_id):
    """
    View for Config/Harvester Log file
    :param request:
    :param config_id: Harvester Config
    :return:
    """
    config = get_object_or_404(Config, pk=config_id)
    # find log file from config name
    log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
    log_name = config.name.strip().replace(" ", "_")
    log_file = os.path.join(log_dir, "{}.log").format(log_name)
    log_exists = os.path.isfile(os.path.join(log_file))
    if log_exists:
        with open(log_file, 'r') as f:
            # display tail of log
            log_text = "\n".join(tailer.tail(f, 40))
    else:
        log_text = "No log found!"

    return render(request, 'harvester/admin_log.html',{
            'app_label': "harvester",
            'harvester_name': config.name,
            'log_text': log_text,
    })