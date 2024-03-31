from sqlalchemy import create_engine
from models import Base
from database_config import load_db_conf

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
    Base.metadata.create_all(engine)
