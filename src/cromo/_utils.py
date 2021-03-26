import logging
import os
import re
from pathlib import Path
import platform
import click
import requests
import validators
import cromo

from cromo.constants import CROMO_DIR, LOG_FILE
MODEL_ID_URI = "https://w3id.org/okn/i/mint/"
__DEFAULT_MINT_API_CREDENTIALS_FILE__ = "~/.mint/credentials"


def obtain_id(url):
    if validators.url(url):
        return url.split('/')[-1]


def first_line_new(resource, i=""):
    click.echo("======= {} ======".format(resource))
    click.echo("The actual values are:")

def make_log_file():
    if os.path.exists(Path(CROMO_DIR) / LOG_FILE):
        return True
    try:
        if not os.path.exists(Path(CROMO_DIR)):
            os.mkdir(CROMO_DIR)
        if not os.path.exists(Path(CROMO_DIR) / LOG_FILE):
            with open(Path(CROMO_DIR) / LOG_FILE, 'w') as fp:
                pass

        init_logger()
        return True
    except Exception as e:
        click.secho("WARNING: Could not make log file: \"{}\"".format(e),fg="yellow")
        return False

def log_system_info(logger):
    log = logging.getLogger(logger)
    log.info("Log file created")
    try:
        plat_obj = {'name': platform.system(), 'data': {'version': platform.version(),
                                                       'release': platform.release(),
                                                       'platform': platform.platform()}}
    except Exception as e:
        log.warning("os obj got attribute error while making os object")
        try:
            plat_obj = {'name': os.name}
        except Exception as e:
            plat_obj = {'name': "Unknown os"}

    log.info("OS: {}".format(plat_obj))
    log.info("cromo Version: {}".format(cromo.__version__))

def log_variable(logger, var, name="variable"):
    """
    Given a logger log a debug variable, logs variable's content and type. Optional: enter name field to give a
    descriptive name
    :param logger:
    :param var:
    :param name:
    :return:
    """
    logger.debug("{}: {}".format(name,{'content': var, 'type': type(var).__name__}))

def log_command(logger, command_name, **kwargs):
    """
    List the current command, enter option variables of command as kwargs to display what the inputs are.
    Ex: log_command(logging, "start", name="name", image="image")
    :param logger:
    :param command_name:
    :param kwargs:
    :return:
    """
    logger.info("<=================>")
    if len(kwargs) > 0:
        inp = {}
        for key, value in kwargs.items():
            inp[key] = {'value': value, 'type': type(value).__name__}

        logger.info("Command: {}".format({'name': command_name, 'command_parameters': inp }))
    else:
        logger.info("Command: {}".format(command_name))

def get_cromo_logger():
    return logging.getLogger(cromo.__name__)


def init_logger():
    logger = logging.getLogger(cromo.__name__)
    if os.path.exists(Path(CROMO_DIR) / LOG_FILE):
        handler = logging.FileHandler(Path(CROMO_DIR) / LOG_FILE)
    elif os.path.exists(LOG_FILE):
        handler = logging.FileHandler(LOG_FILE)
    else:
        handler = logging.StreamHandler()
    formatter = logging.Formatter("%(name)-5s %(filename)-18s %(levelname)-8s %(message)s")
    handler.setFormatter(formatter)

    #Remove all other handlers before adding new one
    for i in logger.handlers:
        logger.removeHandler(i)

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


def get_latest_version():
    try:
        return requests.get("https://pypi.org/pypi/cromo/json").json()["info"]["version"]
    except Exception as e:
        raise e

def find_dir(name, path):
    for root, dirs, files in os.walk(path):
        if os.path.basename(root) == name:
            return root

def parse(value):
    try:
        return int(value)
    except:
        return value
