import logging
import random
import math
from datetime import datetime, timedelta

from zoneinfo import ZoneInfo
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from delivery_system.db.dao.client_dao import ClientDAO
from delivery_system.db.dao.courier_dao import CourierDAO
from delivery_system.db.dao.order_dao import OrderDAO
from delivery_system.db.models.order_model import OrderModel
from delivery_system.db.models.enums import OrderStatus, TransportType

logger = logging.getLogger(__name__)
fake = Faker("ru_RU")


class OrderMaker:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.client_dao = ClientDAO(session)
        self.courier_dao = CourierDAO(session)
        self.order_dao = OrderDAO(session)

    def _calculate_distance(self, lat1, lon1, lat2, lon2) -> float:
        """Haversine estimation for Moscow latitudes."""
        # 1 deg lat ~ 111 km, 1 deg lon ~ 62 km
        d_lat = (lat2 - lat1) * 111.0
        d_lon = (lon2 - lon1) * 62.0 
        return math.sqrt(d_lat**2 + d_lon**2)

    def _calculate_price(self, distance_km: float, transport: TransportType) -> float:
        """Dynamic pricing logic."""
        base = 150.0
        
        # Ставки за км зависят от типа
        if transport == TransportType.FOOT:
            rate = 20.0 # Дешевле за км, но расстояние маленькое
        elif transport == TransportType.BICYCLE:
            rate = 25.0
        else:
            rate = 40.0 # Авто дорогое

        price = base + (distance_km * rate)
        
        # Коэффициент сложности
        if transport == TransportType.CAR: price *= 1.2

        return round(price, 2)

    def _generate_pickup_point(self, client_lat: float, client_lon: float, transport: TransportType) -> tuple[float, float]:
        """
        Generate a location based on courier capabilities relative to the client.
        """
        # 1. Определяем максимальный радиус поиска ресторана (в км)
        if transport == TransportType.FOOT:
            min_r, max_r = 0.3, 2.5  # Пеший: от 300м до 2.5км
        elif transport == TransportType.BICYCLE:
            min_r, max_r = 1.0, 7.0  # Вело: от 1км до 7км
        else:
            min_r, max_r = 3.0, 25.0 # Авто: далеко

        # 2. Генерируем случайное расстояние и угол
        dist_km = random.uniform(min_r, max_r)
        angle_rad = random.uniform(0, 2 * math.pi)

        # 3. Переводим км в градусы (смещаем точку от клиента)
        # d_lat = dist * cos(a) / 111
        # d_lon = dist * sin(a) / 62
        delta_lat = (dist_km * math.cos(angle_rad)) / 111.0
        delta_lon = (dist_km * math.sin(angle_rad)) / 62.0

        return client_lat + delta_lat, client_lon + delta_lon

    async def create_random_order(self) -> None:
        clients = await self.client_dao.get_all_ids()
        couriers = await self.courier_dao.get_all_ids()

        if not clients or not couriers:
            return

        # 1. Выбираем Исполнителя и Клиента
        courier_id, c_transport = random.choice(couriers)
        client_id, c_lat, c_lon = random.choice(clients)

        # 2. Генерируем адрес
        p_lat, p_lon = self._generate_pickup_point(c_lat, c_lon, c_transport)
        
        pickup_address = f"г. Москва, {fake.street_name()}, д. {fake.building_number()} ({fake.company()})"

        # 3. Фактический расчет дистанции (для точности)
        dist = self._calculate_distance(p_lat, p_lon, c_lat, c_lon)
        price = self._calculate_price(dist, c_transport)

        # 4. Время выполнения
        speed = {TransportType.FOOT: 4.5, TransportType.BICYCLE: 12.0, TransportType.CAR: 28.0}[c_transport]
        duration_hours = dist / speed
        duration_sec = int(duration_hours * 3600) + random.randint(300, 1200) # +5-20 мин на передачу
        
        moscow_tz = ZoneInfo("Europe/Moscow")
        finished_at = datetime.now(moscow_tz)
        created_at = finished_at - timedelta(seconds=duration_sec)

        # 5. Сохраняем
        order = OrderModel(
            client_id=client_id,
            courier_id=courier_id,
            status=OrderStatus.DELIVERED,
            pickup_address=pickup_address,
            pickup_lat=p_lat,
            pickup_lon=p_lon,
            delivery_lat=c_lat,
            delivery_lon=c_lon,
            distance_km=round(dist, 2),
            price=price,
            created_at=created_at,
            finished_at=finished_at
        )
        await self.order_dao.add(order)
        await self.session.commit()
        
        logger.info(f"Order: {c_transport.value} | {round(dist, 1)}km | {price}RUB")
