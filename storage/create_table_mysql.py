from sqlalchemy import create_engine
from models import Base
from load_config import load_app_conf
import time

DATA, _, _, _  = load_app_conf()

# DATABASE VARIABLES
USER = DATA['user']
PASSWORD = DATA['password']
HOST = DATA['hostname']
PORT = DATA['port']
DB = DATA['db']

# Modify the create_engine function call to adjust connection pooling options
engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}", echo=True)

def create_database():
    try:
        Base.metadata.create_all(engine)
    except Exception as e:
        print('Failed to connect error: ', str(e))

