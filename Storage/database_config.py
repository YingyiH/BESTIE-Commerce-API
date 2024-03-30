import yaml

def load_db_conf():

    with open('conf_app.yml', 'r') as f:
        conf_app = yaml.safe_load(f.read())
        data = conf_app['datastore']
        event = conf_app['events']
        retry_logs = conf_app['retry_logs']

    return data['user'], data['password'], data['hostname'], data['port'], data['db'], event['hostname'], event['port'], event['topic'], retry_logs['max_retry'],retry_logs['delay_seconds'], retry_logs['current_retry']

print(load_db_conf())