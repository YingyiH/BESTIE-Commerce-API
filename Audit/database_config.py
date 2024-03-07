import yaml

def load_db_conf():

    with open('conf_app.yml', 'r') as f:
        conf_app = yaml.safe_load(f.read())
        event = conf_app['events']

    return event['hostname'], event['port'], event['topic']

print(load_db_conf())