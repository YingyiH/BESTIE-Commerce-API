import logging
import logging.config
import yaml
import os


# Load configuration file:
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    conf_app_file = "/config/conf_app.yml"
    conf_log_file = "/config/conf_log.yml"
else:
    print("In Dev Environment")
    conf_app_file = "conf_app.yml"
    conf_log_file = "conf_log.yml"

# Read configuration file:
def load_app_conf():

    with open(conf_app_file, 'r') as f:
        app_config = yaml.safe_load(f.read())
        seconds= app_config['scheduler']['period_sec']
        event_url = app_config['eventstore']['url']
        default_count = app_config['default_value']['config_value']
        app_conf_file = conf_app_file
        events = app_config['events']

    return seconds, event_url, default_count, app_conf_file, events

def load_log_conf():

    with open(conf_log_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')
        log_conf_file = conf_log_file

    return logger, log_conf_file

