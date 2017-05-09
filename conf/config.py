import configparser
import os


def get_config(key_value=None, path=None):
    """
    Wrapper for Python config parser.
    Allows checking values of the global config file
    :param key_value: category of config
    :param path: optionally the global config can be changed
    :return:
    """
    config = configparser.ConfigParser()
    if path is None:
        # default assumption is that the config is in the same folder
        directory = os.path.dirname(__file__)
        path = os.path.join(directory, 'global_config.ini')
    config.read(path)
    if key_value is None:
        return config
    elif key_value in config:
        return config[key_value]
    return None
