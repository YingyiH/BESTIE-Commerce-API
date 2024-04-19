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
        conf_app = yaml.safe_load(f.read())
        data = conf_app['datastore']
        event = conf_app['events']
        retry_logs = conf_app['retry_logs']
        default_anomaly = conf_app['default_anomaly']
        app_conf_file = conf_app_file

    return data, event, retry_logs, default_anomaly, app_conf_file

def load_log_conf():
    with open(conf_log_file, 'r') as f:
        log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
        logger = logging.getLogger('basicLogger')
        log_conf_file = conf_log_file

    return logger, log_conf_file

 