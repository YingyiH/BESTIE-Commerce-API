from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func


class Base(DeclarativeBase):
    pass



class Msg(Base):
    __tablename__ = 'msg_create'
    id = mapped_column(
        String(26), primary_key=True)
    message = mapped_column(String(255), nullable=False)
    code = mapped_column(
        String(4), nullable=False)
    date = mapped_column(DateTime, nullable=False)

    def to_dict(self, full=False):
        data = self.__dict__

        keys = ['message', 'code', 'time']

        return {k: v for k, v in data.items() if k in keys}



