from typing import Optional

from pydantic import ConfigDict
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
    MODEL_PRICE: int
    model_config = SettingsConfigDict(env_file='.env',
                                      extra="ignore")


class JWTSettings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ACCESS_COOKIE_NAME: str
    JWT_COOKIE_SECURE: bool = False
    JWT_COOKIE_CSRF_PROTECT: bool = False
    JWT_ALGORITHM: str = 'HS256'

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True
    )
