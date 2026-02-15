from enum import StrEnum
from functools import lru_cache
from typing import Final

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.logger import CustomLogger


class AppStand(StrEnum):
    LOCAL = "local"
    DEV = "dev"
    RC = "rc"
    PROD = "prod"
    TEST = "test"


class ServiceName(StrEnum):
    MAIL = "mail"


class _Settings(BaseSettings):
    APP_DEBUG: bool = False
    APP_STAND: AppStand = AppStand.LOCAL
    APP_RELEASE: str = "not-set"
    APP_NAME: ServiceName = ServiceName.MAIL

    # Postgress
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_POOL_SIZE: int = 10
    POSTGRES_ECHO_POOL: str | bool = False
    POSTGRES_CONNECTION_RETRY_PERIOD_SEC: float = 5.0
    POSTGRES_STATEMENT_TIMEOUT: int = 60000

    @property
    def POSTGRES_URL(self) -> str:
        return "postgresql+asyncpg://{}:{}@{}:{}/{}".format(
            self.POSTGRES_USER,
            self.POSTGRES_PASSWORD,
            self.POSTGRES_HOST,
            self.POSTGRES_PORT,
            self.POSTGRES_DB,
        )

    # Rabbit
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str

    @property
    def RABBITMQ_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"
            f"?name={self.APP_NAME}"
        )

    SMTP_HOST: str
    SMTP_PORT: int = 587
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_USE_TLS: bool = True

    MAIL_FROM: str

    @staticmethod
    def configure_logging():
        return CustomLogger.make_logger()

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_ignore_empty=True,
    )


@lru_cache
def get_settings(env_file: str = ".env") -> _Settings:
    return _Settings(_env_file=env_file)


SETTINGS: Final[_Settings] = get_settings()
