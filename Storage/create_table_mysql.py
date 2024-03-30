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
    echo=True,
    pool_size=20,        # Adjust the pool size as needed based on your application's requirements
    pool_recycle=3600,   # Set the pool_recycle to a value greater than the wait_timeout of your database server to avoid connection timeouts
    pool_pre_ping=True   # Enable pool_pre_ping to automatically check and refresh connections before use to prevent stale connections
)

# engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}', echo=True)


def create_database():
    Base.metadata.create_all(engine)
