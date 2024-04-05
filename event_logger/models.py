from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func


class Base(DeclarativeBase):
    pass

class Msg(Base):
    __tablename__ = 'msg_create'

    msg_code = mapped_column(String(50), nullable = True)
    msg_id =  mapped_column(String(50), primary_key = True)
    event_num = mapped_column(Integer, nullable = True)
    msg_string = mapped_column(String(50), nullable = True)
    last_updated = mapped_column(DateTime, nullable = False, default = func.now())



