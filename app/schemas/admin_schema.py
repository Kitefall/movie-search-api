from decimal import Decimal

from pydantic import BaseModel


class AdminCoinsSchema(BaseModel):
    amount: Decimal
    target_user_id: int


class AdminGetTransactionSchema(BaseModel):
    target_user_id: int
