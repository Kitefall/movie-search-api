from enum import Enum

from sqlalchemy import Column
from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from .base import Base


class PredictionType(Enum):
    MODEL_SEND_REQUEST = "Отправлен запрос к модели"
    MODEL_RECEIVED_PREDICT = "Получен результат работы модели"
    MODEL_ERROR = "Ошибка при обработке"


class HistoryPredict(Base):
    __tablename__ = 'history_predictions'

    id = Column(Integer,
                primary_key=True,
                index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='history_predict')
    data = Column(String)
    result = Column(String)
    prediction_type = Column(SqlEnum(PredictionType, native_enum=True),
                             nullable=False)
    price = Column(Numeric(9, 2), nullable=False)

    def __repr__(self):
        return f'<user_id={self.user_id}:Предсказание={self.data}'
