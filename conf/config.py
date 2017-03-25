import configparser
import pathlib
import os


def get_config(key_value=None, path=None):
    config = configparser.ConfigParser()
    if path is None:
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'global_config.ini')
    config.read(path)
    if key_value is None:
        return config
    elif key_value in config:
        return config[key_value]
    return None
