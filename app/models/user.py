from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class Role(Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,
                primary_key=True,
                index=True)
    name = Column(String,
                  nullable=False)
    password = Column(String,
                      nullable=False)
    email = Column(String,
                   unique=True,
                   index=True,
                   nullable=False)
    role = Column(SqlEnum(Role, native_enum=True),
                  nullable=False,
                  default=Role.USER)
    history_predict = relationship('HistoryPredict',
                                   back_populates='user')
    coin_account = relationship('CoinAccount',
                                back_populates='user',
                                uselist=False,
                                cascade="all, delete-orphan")
