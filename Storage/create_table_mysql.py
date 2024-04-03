from sqlalchemy import create_engine
from models import Base
from load_config import load_db_conf
import time

DATA, _, _  = load_db_conf()

# DATABASE VARIABLES
USER = DATA['user']
PASSWORD = DATA['password']
HOST = DATA['hostname']
PORT = DATA['port']
DB = DATA['db']

# Modify the create_engine function call to adjust connection pooling options
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}", 
    echo=True
)

# engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}', echo=True)


def create_database():
    connecting = True
    counter = 0
    while connecting:
        try:
            Base.metadata.create_all(engine)
            connecting = False
        except Exception as e:
            print('Failed to connect error: ', str(e))
            print(f'Attempt {counter}')


