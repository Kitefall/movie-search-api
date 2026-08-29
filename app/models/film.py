from sqlalchemy import Column, Integer, String

from .base import Base


class Film(Base):
    __tablename__ = 'films'

    id = Column(Integer,
                primary_key=True,
                index=True)
    title = Column(String, nullable=False)
    plot = Column(String, nullable=False)
    genre = Column(String)
