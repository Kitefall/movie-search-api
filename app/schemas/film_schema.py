from pydantic import BaseModel, ConfigDict


class FilmSchema(BaseModel):
    title: str
    plot: str
    genre: str

    model_config = ConfigDict(from_attributes=True)
