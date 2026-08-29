from decimal import Decimal
from typing import Optional

from models.history_predict import PredictionType
from pydantic import BaseModel


class HistoryPredictBase(BaseModel):
    user_id: int
    data: str
    result: Optional[str]
    prediction_type: PredictionType
    price: Decimal


class HistoryPredictMessage(HistoryPredictBase):
    id: int
    status: Optional[str]
