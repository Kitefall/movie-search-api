from sqlalchemy import Column, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from .base import Base


class CoinAccount(Base):
    __tablename__ = 'coin_accounts'

    user_id = Column(Integer,
                     ForeignKey('users.id'),
                     primary_key=True,
                     index=True)
    balance = Column(Numeric(9, 2), default=0.00, nullable=False)
    user = relationship('User', back_populates='coin_account')
