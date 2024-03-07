from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func


class Base(DeclarativeBase):
    pass

class Stat(Base):
    __tablename__ = 'stat_create'

    reading_id =  mapped_column(String(50), primary_key = True)
    num_products = mapped_column(Integer, nullable = True)
    num_reviews = mapped_column(Integer, nullable = True)
    num_onsale_products = mapped_column(Integer, nullable = True)
    max_price = mapped_column(Integer, nullable = True)
    last_updated = mapped_column(DateTime, nullable = False, default = func.now())



