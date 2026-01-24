import logging
import random
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_system.db.dao.client_dao import ClientDAO
from delivery_system.db.dao.courier_dao import CourierDAO
from delivery_system.db.models.client_model import ClientModel
from delivery_system.db.models.courier_model import CourierModel
from delivery_system.db.models.enums import TransportType

logger = logging.getLogger(__name__)
fake = Faker("ru_RU")

MOSCOW_BOUNDS = {
    "lat_min": 55.55,
    "lat_max": 55.90,
    "lon_min": 37.35,
    "lon_max": 37.85,
}


class CityPopulator:
    """Service to populate database with initial fake data."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.client_dao = ClientDAO(session)
        self.courier_dao = CourierDAO(session)

    def _get_random_coords(self) -> tuple[float, float]:
        """Generate random coordinates within Moscow."""
        lat = random.uniform(MOSCOW_BOUNDS["lat_min"], MOSCOW_BOUNDS["lat_max"])
        lon = random.uniform(MOSCOW_BOUNDS["lon_min"], MOSCOW_BOUNDS["lon_max"])
        return lat, lon

    async def populate_clients(self, target_count: int = 100) -> None:
        """Create clients if not enough exist."""
        current_count = await self.client_dao.get_count()
        if current_count >= target_count:
            logger.info(f"Clients already populated ({current_count}).")
            return

        needed = target_count - current_count
        logger.info(f"Generating {needed} new clients...")

        new_clients = []
        for _ in range(needed):
            lat, lon = self._get_random_coords()

            street = fake.street_name()
            house = fake.building_number()
            if random.random() > 0.8:
                house += f" к{random.randint(1, 4)}"
            
            address = f"г. Москва, {street}, д. {house}"

            client = ClientModel(
                name=fake.name(),
                address=address,
                lat=lat,
                lon=lon,
            )
            new_clients.append(client)

        await self.client_dao.add_bulk(new_clients)
        logger.info("Clients generated.")

    async def populate_couriers(self, target_count: int = 20) -> None:
        """Create couriers if not enough exist."""
        current_count = await self.courier_dao.get_count()
        if current_count >= target_count:
            logger.info(f"Couriers already populated ({current_count}).")
            return

        needed = target_count - current_count
        logger.info(f"Generating {needed} new couriers...")

        new_couriers = []
        for _ in range(needed):
            # Веса: Пеших 50%, Вело 30%, Авто 20%
            transport = random.choices(
                list(TransportType), 
                weights=[50, 30, 20], 
                k=1
            )[0]
            
            courier = CourierModel(
                name=fake.name(),
                transport_type=transport,
            )
            new_couriers.append(courier)

        await self.courier_dao.add_bulk(new_couriers)
        logger.info("Couriers generated.")

    async def ensure_population(self) -> None:
        """Main entry point to ensure data exists."""
        await self.populate_clients(100)
        await self.populate_couriers(20)
        await self.session.commit()
