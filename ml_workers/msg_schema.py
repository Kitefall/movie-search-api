from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class PredictionType(Enum):
    MODEL_SEND_REQUEST = "Отправлен запрос к модели"
    MODEL_RECEIVED_PREDICT = "Получен результат работы модели"
    MODEL_ERROR = "Ошибка при обработке"


class HistoryPredictMessage(BaseModel):
    id: int
    user_id: int
    data: str
    result: Optional[str]
    prediction_type: PredictionType
    price: Decimal
    status: Optional[str]
