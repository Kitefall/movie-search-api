from decimal import Decimal

from pydantic import BaseModel


class TopUpRequest(BaseModel):
    amount: Decimal
