from sqlalchemy import create_engine
from models import Base
from database_config import load_db_conf

USER, PASSWORD, HOST, PORT, DB, KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC= load_db_conf()

engine = create_engine(f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}', echo=True)


def create_database():
    Base.metadata.create_all(engine)
