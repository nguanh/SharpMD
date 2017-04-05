from django.shortcuts import render
from django.shortcuts import get_object_or_404
import os
import tailer
from .models import Config
PROJECT_DIR = os.path.dirname(__file__)


def log(request, config_id):
    config = get_object_or_404(Config, pk=config_id)
    log_dir = os.path.join(os.path.dirname(PROJECT_DIR), "logs")
    log_name = config.name.strip().replace(" ", "_")
    log_file = os.path.join(log_dir, "{}.log").format(log_name)
    log_exists = os.path.isfile(os.path.join(log_file))
    if log_exists:
        log_text = tailer.tail(log_file,40)
    else:
        log_text = "No log found!"

    return render(request, 'harvester/admin_log.html',{
            'app_label': "harvester",
            'harvester_name': config.name,
            'log_text': log_text,
    })