import yaml

def load_db_conf():

    with open('conf_app.yml', 'r') as f:
        conf_app = yaml.safe_load(f.read())
        data = conf_app['datastore']
        event = conf_app['events']
        retry_logs = conf_app['retry_logs']

    return data, event, retry_logs

print(load_db_conf())