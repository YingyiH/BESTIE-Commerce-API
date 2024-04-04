import logging
import logging.config
import yaml
import os

# Load configuration file:
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    conf_app_file = "/config/audit_log/conf_app.yml"
    conf_log_file = "/config/audit_log/conf_log.yml"
else:
    print("In Dev Environment")
    conf_app_file = "conf_app.yml"
    conf_log_file = "conf_log.yml"

# Read configuration file:
def load_app_conf():

    with open(conf_app_file, 'r') as f:
        conf_app = yaml.safe_load(f.read())
        event = conf_app['events']
        app_conf_file = conf_app_file

    return event['hostname'], event['port'], event['topic'], app_conf_file

def load_log_conf():

    with open(conf_log_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')
        log_conf_file = conf_log_file

    return logger, log_conf_file