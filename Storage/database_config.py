import yaml

def load_db_conf():

    with open('conf_app.yml', 'r') as f:
        conf_app = yaml.safe_load(f.read())
        data = conf_app['datastore']
        event = conf_app['events']

    return data['user'], data['password'], data['hostname'], data['port'], data['db'], event['hostname'], event['port'], event['topic']

print(load_db_conf())