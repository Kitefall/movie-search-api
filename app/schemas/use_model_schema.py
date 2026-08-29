from pydantic import BaseModel


class InputDataModel(BaseModel):
    data: str
