from sqlalchemy import create_engine
from models import Base
import os
import yaml

with open('conf_app.yml', 'r') as f:
        app_config = yaml.safe_load(f.read())
DATABASE = app_config['datastore']['filename']

engine = create_engine(f"sqlite:///{DATABASE}", echo=True)


def create_database():
    if not (os.path.exists(f"./{DATABASE}")):
        Base.metadata.create_all(engine)
