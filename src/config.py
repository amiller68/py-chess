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


class Secrets:
    """Container for sensitive configuration values"""

    service_secret: str
    google_client_id: str
    google_client_secret: str

    def __str__(self) -> str:
        def mask_secret(secret: str | None) -> str:
            if not secret:
                return "None"
            secret_str = str(secret)
            if len(secret_str) < 6:
                return "***"
            return f"{secret_str[:3]}...{secret_str[-3:]}"

        return (
            f"Secrets(service_secret={mask_secret(self.service_secret)}, "
            f"google_client_id={self.google_client_id}, "
            f"google_client_secret={mask_secret(self.google_client_secret)})"
        )

    def __init__(self) -> None:
        # Service secret - auto-generate if not provided
        self.service_secret = empty_to_none("SERVICE_SECRET") or ""
        if not self.service_secret:
            import secrets

            self.service_secret = secrets.token_urlsafe(32)
            print(f"Generated SERVICE_SECRET: {self.service_secret[:8]}...")

        # Google OAuth credentials
        self.google_client_id = empty_to_none("GOOGLE_O_AUTH_CLIENT_ID") or ""
        self.google_client_secret = empty_to_none("GOOGLE_O_AUTH_CLIENT_SECRET") or ""

        if not self.google_client_id:
            raise ConfigException(
                ConfigExceptionType.missing_env_var,
                "GOOGLE_O_AUTH_CLIENT_ID environment variable must be set",
            )
        if not self.google_client_secret:
            raise ConfigException(
                ConfigExceptionType.missing_env_var,
                "GOOGLE_O_AUTH_CLIENT_SECRET environment variable must be set",
            )


class Config:
    """Application configuration loaded from environment variables"""

    dev_mode: bool
    host_name: str
    listen_address: str
    listen_port: int
    auth_redirect_uri: str
    postgres_url: str
    postgres_async_url: str
    debug: bool
    secrets: Secrets

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
        self.auth_redirect_uri = os.getenv(
            "AUTH_REDIRECT_URI", f"{self.host_name}/auth/google/callback"
        )

        # PostgreSQL URL
        postgres_url = empty_to_none("POSTGRES_URL")
        if not postgres_url:
            raise ConfigException(
                ConfigExceptionType.missing_env_var,
                "POSTGRES_URL environment variable must be set",
            )
        self.postgres_url = postgres_url
        self.postgres_async_url = postgres_url.replace("postgresql://", "postgresql+asyncpg://")

        # Debug mode
        self.debug = os.getenv("DEBUG", "True") == "True"

        # Load secrets
        self.secrets = Secrets()
