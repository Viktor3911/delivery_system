from sqlalchemy import select

from delivery_system.db.dao.base import BaseDAO
from delivery_system.db.models.client_model import ClientModel


class ClientDAO(BaseDAO):
    """DAO for Client models."""

    async def add_bulk(self, clients: list[ClientModel]) -> None:
        """Efficiently add multiple clients."""
        self.session.add_all(clients)
        # Flush нужен, чтобы получить ID, если они генерируются БД,
        # но в нашем случае ID - UUID, генерируемые на стороне БД или кода.
        # Commit будет вызван снаружи.
        await self.session.flush()

    async def get_all_ids(self) -> list:
        """Get all client IDs and their coordinates for order generation."""
        # Нам нужны координаты сразу, чтобы не делать лишних запросов при генерации заказа
        query = select(ClientModel.id, ClientModel.lat, ClientModel.lon)
        result = await self.session.execute(query)
        return result.all()
