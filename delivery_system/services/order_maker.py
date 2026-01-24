import logging
import random
import math
from datetime import datetime, timedelta, timezone

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_system.db.dao.client_dao import ClientDAO
from delivery_system.db.dao.courier_dao import CourierDAO
from delivery_system.db.dao.order_dao import OrderDAO
from delivery_system.db.models.order_model import OrderModel
from delivery_system.db.models.enums import OrderStatus, TransportType

logger = logging.getLogger(__name__)
fake = Faker("ru_RU")

MOSCOW_BOUNDS = {
    "lat_min": 55.55, "lat_max": 55.90,
    "lon_min": 37.35, "lon_max": 37.85,
}


class OrderMaker:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.client_dao = ClientDAO(session)
        self.courier_dao = CourierDAO(session)
        self.order_dao = OrderDAO(session)

    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Rough estimation of distance in KM using Haversine-like formula for short distances."""
        # 1 deg lat ~ 111 km
        # 1 deg lon ~ 111 * cos(lat) km
        d_lat = (lat2 - lat1) * 111.0
        d_lon = (lon2 - lon1) * 111.0 * 0.56  # cos(55.7) approx 0.56
        return math.sqrt(d_lat**2 + d_lon**2)

    def _calculate_price(self, distance_km: float, transport: TransportType) -> float:
        base_price = 150.0
        km_price = 30.0
        price = base_price + (distance_km * km_price)
        
        # Наценка за скорость/амортизацию
        if transport == TransportType.CAR:
            price *= 1.5
        elif transport == TransportType.BICYCLE:
            price *= 1.1
            
        return round(price, 2)

    async def create_random_order(self) -> None:
        """Creates a single random completed order."""
        # 1. Получаем участников (ID и метаданные)
        clients = await self.client_dao.get_all_ids()
        couriers = await self.courier_dao.get_all_ids()

        if not clients or not couriers:
            logger.warning("No clients or couriers found. Skipping order generation.")
            return

        # Выбираем случайных
        client_row = random.choice(clients) # (id, lat, lon)
        courier_row = random.choice(couriers) # (id, transport_type)

        client_id, client_lat, client_lon = client_row
        courier_id, courier_transport = courier_row

        # 2. Генерируем точку старта
        pickup_lat = random.uniform(MOSCOW_BOUNDS["lat_min"], MOSCOW_BOUNDS["lat_max"])
        pickup_lon = random.uniform(MOSCOW_BOUNDS["lon_min"], MOSCOW_BOUNDS["lon_max"])

        company_name = fake.company() 
        pickup_street = fake.street_name()
        pickup_house = fake.building_number()
        pickup_address = f"г. Москва, {pickup_street}, д. {pickup_house} ({company_name})"

        # 3. Считаем математику
        distance = self._calculate_distance(pickup_lat, pickup_lon, client_lat, client_lon)
        price = self._calculate_price(distance, courier_transport)

        # 4. Считаем время
        # Средняя скорость: Пеший 5 км/ч, Авто 25 км/ч (пробки)
        speed = 5
        if courier_transport == TransportType.BICYCLE:
            speed = 12
        if courier_transport == TransportType.CAR:
            speed = 25
        
        duration_hours = distance / max(speed, 1)
        duration_seconds = int(duration_hours * 3600) + random.randint(300, 1200)

        finished_at = datetime.now(timezone.utc)
        created_at = finished_at - timedelta(seconds=duration_seconds)

        # 5. Собираем модель
        order = OrderModel(
            client_id=client_id,
            courier_id=courier_id,
            status=OrderStatus.DELIVERED,
            pickup_address=pickup_address,
            pickup_lat=pickup_lat,
            pickup_lon=pickup_lon,
            delivery_lat=client_lat,
            delivery_lon=client_lon,
            distance_km=round(distance, 2),
            price=price,
            created_at=created_at,
            finished_at=finished_at
        )

        await self.order_dao.add(order)
        await self.session.commit()
        
        logger.info(f"Order created! {courier_transport.value} -> {round(distance, 1)}km | {price} RUB")