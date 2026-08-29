from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class RabbitmqSettings(BaseSettings):
    RABBIT_USER: Optional[str] = None
    RABBIT_PASS: Optional[str] = None
    RABBIT_NAME: Optional[str] = None
    RABBIT_PORT: Optional[str] = None
    REQUEST_QUEUE: Optional[str] = None
    RESPONSE_QUEUE: Optional[str] = None

    @property
    def RABBITMQ_URL(self):
        return (f"amqp://{self.RABBIT_USER}:"
                f"{self.RABBIT_PASS}@{self.RABBIT_NAME}:{self.RABBIT_PORT}/")

    model_config = SettingsConfigDict(env_file='.env',
                                      extra="ignore")


class ModelSettings(BaseSettings):
    COUNT_FILMS: int
