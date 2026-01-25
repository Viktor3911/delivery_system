import logging
from alembic.config import Config
from alembic import command
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from delivery_system.settings import settings


async def create_db_if_not_exists(db_name: str) -> None:
    """создает базу данных с указанным именем, если она еще не существует."""
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
        )
        exists = result.scalar()
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{db_name}" ENCODING "utf8"'))

    await engine.dispose()


async def create_database() -> None:
    """Инициализация всех необходимых баз данных проекта."""
    await create_db_if_not_exists(settings.db_base)

    await create_db_if_not_exists("redash_metadata")


def run_migrations() -> None:
    """
    Run Alembic migrations programmatically.
    This ensures the DB schema is up-to-date when the container starts.
    """
    logger = logging.getLogger(__name__)
    logger.info("Running pending migrations...")

    alembic_cfg_path = "alembic.ini"
    
    if not Path(alembic_cfg_path).exists():
        raise FileNotFoundError(f"Alembic config not found at {alembic_cfg_path}")

    try:
        alembic_cfg = Config(alembic_cfg_path)
        alembic_cfg.attributes['configure_logger'] = False
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
