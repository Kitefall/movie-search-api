from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, DateTime
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from .base import Base


class TransactionType(Enum):
    ADD_COINS = 'Пополнение баланса пользователем'
    WRITE_OFF = 'Списание монет'
    ADMIN_ADD_COINS = 'Пополнение баланса администратором'
    ADMIN_WRITE_OFF = 'Списание монет администратором'
    BACK_COINS = 'Возврат монет'


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer,
                primary_key=True,
                index=True)
    transaction_type = Column(SqlEnum(TransactionType,
                                      native_enum=True),
                              nullable=False)
    initiator_id = Column(Integer, ForeignKey('users.id'))
    target_user_id = Column(Integer, ForeignKey('users.id'))
    initiator = relationship('User',
                             foreign_keys=[initiator_id],
                             )
    target_user = relationship('User',
                               foreign_keys=[target_user_id],
                               )
    timestamp = Column(DateTime(timezone=True),
                       default=lambda: datetime.now(timezone.utc))
    transaction_amount = Column(Numeric(9, 2), nullable=False)

    def __repr__(self):
        return f'''<Transaction id={self.id}:
                type={self.transaction_type.name}
                initiator_id={self.initiator_id}
                target_user_id={self.target_user_id}
                timestamp={self.timestamp.isoformat()}
                amount={float(self.transaction_amount)}>'''
