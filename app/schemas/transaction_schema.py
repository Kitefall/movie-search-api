from decimal import Decimal

from models.transactions import TransactionType
from pydantic import BaseModel


class TransactionBase(BaseModel):
    initiator_id: int
    target_user_id: int
    transaction_amount: Decimal
    transaction_type: TransactionType
