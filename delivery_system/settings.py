import enum

from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL


class LogLevel(str, enum.Enum):
    """Possible log levels."""
    INFO = "INFO"
    DEBUG = "DEBUG"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Settings(BaseSettings):
    """
    Application settings.
    """
    # Generator settings
    generator_delay: float = 1.0  # seconds between orders

    # Database
    db_host: str = "db"
    db_port: int = 5432
    db_user: str = "delivery_user"
    db_pass: str = "delivery_pass"
    db_base: str = "delivery_db"
    db_echo: bool = False

    @property
    def db_url(self) -> URL:
        """
        Assemble async database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def sync_db_url(self) -> str:
        """
        Assemble sync database URL (for Alembic and Pandas).
        """
        return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_base}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="DELIVERY_SYSTEM_",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
