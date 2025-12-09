import os
from enum import Enum as PyEnum

from dotenv import load_dotenv


class ConfigExceptionType(PyEnum):
    missing_env_var = "missing_env_var"
    invalid_env_var = "invalid_env_var"


class ConfigException(Exception):
    def __init__(self, type: ConfigExceptionType, message: str):
        self.message = message
        self.type = type


def empty_to_none(field: str) -> str | None:
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value


class Config:
    """Application configuration loaded from environment variables"""

    dev_mode: bool
    host_name: str
    listen_address: str
    listen_port: int
    postgres_url: str
    postgres_async_url: str
    debug: bool

    def __str__(self) -> str:
        return (
            f"Config(dev_mode={self.dev_mode}, host_name={self.host_name}, "
            f"listen_address={self.listen_address}, listen_port={self.listen_port}, "
            f"postgres_url={self.postgres_url[:20]}..., debug={self.debug})"
        )

    def __init__(self) -> None:
        load_dotenv()

        self.dev_mode = os.getenv("DEV_MODE", "False") == "True"
        self.host_name = os.getenv("HOST_NAME", "http://localhost:8000")
        self.listen_address = os.getenv("LISTEN_ADDRESS", "0.0.0.0")
        self.listen_port = int(os.getenv("LISTEN_PORT", "8000"))

        # PostgreSQL URL (default for dev mode uses port 5434)
        postgres_url = empty_to_none("POSTGRES_URL")
        if not postgres_url:
            if self.dev_mode:
                postgres_url = "postgresql://chess:chess@localhost:5434/chess"
            else:
                raise ConfigException(
                    ConfigExceptionType.missing_env_var,
                    "POSTGRES_URL environment variable must be set",
                )
        self.postgres_url = postgres_url
        self.postgres_async_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://")

        # Debug mode
        self.debug = os.getenv("DEBUG", "True") == "True"
