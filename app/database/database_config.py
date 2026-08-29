from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_NAME: Optional[str] = None
    ADMIN_NAME: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None

    @property
    def DATABASE_URL_asyncpg(self):
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@'
                f'{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')

    @property
    def DATABASE_URL_psycopg(self):
        return (f'postgresql+psycopg2://{self.DB_USER}:'
                f'{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')

    model_config = SettingsConfigDict(env_file='.env',
                                      extra="ignore")


@lru_cache()
def get_settings() -> DatabaseSettings:
    return DatabaseSettings()
