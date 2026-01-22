import asyncio
import logging
import random
import time

from delivery_system.db.utils import run_migrations, create_database
from delivery_system.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Generator service started.")

    # 1. Применяем миграции (Синхронно, перед запуском логики)
    # Это сделает всё "само" при docker compose up
    try:
        # Сначала пробуем создать БД, если её нет (на всякий случай)
        await create_database()
    except Exception as e:
        logger.warning(f"Database creation skipped (might exist): {e}")

    # Запускаем миграции
    run_migrations()

    logger.info("Starting data generation loop...")
    
    # 2. Здесь будет логика генерации (пока заглушка)
    while True:
        logger.info("Simulating new order...")
        # TODO: Вызвать функцию генерации заказа
        await asyncio.sleep(settings.generator_delay)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Generator stopped.")
