import logging
from alembic.config import Config
from alembic import command
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from delivery_system.settings import settings


async def create_database() -> None:
    """Create a database if it does not exist."""
    # Connect to default 'postgres' db to create the target db
    db_url = make_url(str(settings.db_url.with_path("/postgres")))
    engine = create_async_engine(db_url, isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existance = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.db_base}'",
            ),
        )
        database_exists = database_existance.scalar() == 1

        if not database_exists:
            await conn.execute(
                text(
                    f'CREATE DATABASE "{settings.db_base}" ENCODING "utf8"',
                ),
            )
            print(f"Database {settings.db_base} created.")

    await engine.dispose()


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
        command.upgrade(alembic_cfg, "head")
        logger.info("Migrations applied successfully.")
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise
