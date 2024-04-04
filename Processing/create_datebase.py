from sqlalchemy import create_engine
from models import Base
import os
import yaml


# Load configuration file:
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    conf_app_file = "/config/conf_app.yml"
else:
    print("In Dev Environment")
    conf_app_file = "conf_app.yml"


with open(conf_app_file, 'r') as f:
    app_config = yaml.safe_load(f.read())

DATABASE = app_config['datastore']['filename']

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)

def create_database():
    if not (os.path.exists(f"./{DATABASE}")):
        Base.metadata.create_all(engine)
