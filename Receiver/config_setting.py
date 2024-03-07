import yaml
import logging
from logging import config

# Logging and configuration
with open("conf_app.yml", 'r') as f:
    app_config = yaml.safe_load(f.read())
    print(app_config["eventstore"]["product_create"]['url'])

with open('conf_log.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')
