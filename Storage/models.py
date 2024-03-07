from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import BigInteger, Boolean, Integer, String, DateTime, func


class Base(DeclarativeBase):
    pass

class Product(Base):
    __tablename__ = 'product_create'
    id = mapped_column(Integer, primary_key = True)
    product_id =  mapped_column(String(50), nullable = False)
    seller = mapped_column(String(50), nullable = False)
    price = mapped_column(Integer, nullable = False)
    onsale = mapped_column(Boolean, nullable = True)
    description = mapped_column(String(300), nullable = True, default = None)
    date_created = mapped_column(DateTime, nullable = False, default = func.now())
    trace_id = mapped_column(String(50), nullable = False)

class Comment(Base):
    __tablename__ = 'product_review'
    id = mapped_column(Integer, primary_key = True)
    review_id = mapped_column(String(50), nullable=False)
    customer = mapped_column(String(50), nullable=False)
    location = mapped_column(String(50), nullable=False)
    rating = mapped_column(Integer, nullable=False)
    comment = mapped_column(String(300), nullable=True, default = 'Good')
    product_id = mapped_column(String(50), nullable=False)
    date_created = mapped_column(DateTime, nullable = False, default = func.now())
    trace_id = mapped_column(String(50), nullable = False)

