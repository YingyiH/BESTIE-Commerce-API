import yaml
import logging
from logging import config

def load_app_conf():
    with open("conf_app.yml", 'r') as f:
        conf_app = yaml.safe_load(f.read())
        eventstore = conf_app['eventstore']
        events = conf_app['events']
        retry_logs = conf_app['retry_logs']

    return eventstore, events, retry_logs

def load_log_conf():
    with open('conf_log.yml', 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')

    return logger






