import asyncio
import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from delivery_system.db.utils import run_migrations, create_database
from delivery_system.settings import settings
from delivery_system.services.population import CityPopulator
from delivery_system.services.order_maker import OrderMaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def init_infrastructure():
    """Step 1: Create database if not exists."""
    logger.info("Initializing infrastructure...")
    await create_database()

    Path("/tmp/db_ready").touch()
    logger.info("Databases created, readiness flag set.")


async def main_loop():
    """Step 3: Main logic (Population + Generation)."""
    logger.info("Generator service started (Main Loop).")

    engine = create_async_engine(str(settings.db_url), echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    # 1. Заселение
    async with session_factory() as session:
        try:
            populator = CityPopulator(session)
            await populator.ensure_population()
        except Exception as e:
            logger.error(f"Population failed: {e}")

    logger.info("City is populated. Starting order simulation loop...")
    
    # 2. Цикл генерации заказов
    while True:
        async with session_factory() as session:
            try:
                maker = OrderMaker(session)
                await maker.create_random_order()
            except Exception as e:
                logger.error(f"Error generating order: {e}")
        
        await asyncio.sleep(settings.generator_delay)


if __name__ == "__main__":
    try:
        # ЭТАП 1: БД
        asyncio.run(init_infrastructure())

        # ЭТАП 2: Миграции
        run_migrations()

        # ЭТАП 3: Работа
        asyncio.run(main_loop())

    except KeyboardInterrupt:
        logger.info("Generator stopped.")
    except Exception as e:
        logger.critical(f"Critical error at startup: {e}")
