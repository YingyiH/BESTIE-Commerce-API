import yaml
import logging
from logging import config
import os

# Load configuration file:
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    conf_app_file = "/config/receiver/conf_app.yml"
    conf_log_file = "/config/receiver/conf_log.yml"
else:
    print("In Dev Environment")
    conf_app_file = "conf_app.yml"
    conf_log_file = "conf_log.yml"

# Read configuration file:
def load_app_conf():
    with open(conf_app_file, 'r') as f:
        conf_app = yaml.safe_load(f.read())
        eventstore = conf_app['eventstore']
        events = conf_app['events']
        retry_logs = conf_app['retry_logs']
        app_conf_file = conf_app_file

    return eventstore, events, retry_logs, app_conf_file

def load_log_conf():
    with open(conf_log_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')
        log_conf_file = conf_log_file

    return logger, log_conf_file




