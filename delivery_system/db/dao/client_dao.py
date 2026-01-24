from sqlalchemy import select, func

from delivery_system.db.dao.base import BaseDAO
from delivery_system.db.models.client_model import ClientModel


class ClientDAO(BaseDAO):
    """DAO for Client models."""

    async def add_bulk(self, clients: list[ClientModel]) -> None:
        """Efficiently add multiple clients."""
        self.session.add_all(clients)
        await self.session.flush()

    async def get_all_ids(self) -> list:
        """Get all client IDs and their coordinates for order generation."""
        query = select(ClientModel.id, ClientModel.lat, ClientModel.lon)
        result = await self.session.execute(query)

        return result.all()

    async def get_count(self) -> int:
        """Count total clients."""
        query = select(func.count()).select_from(ClientModel)
        result = await self.session.execute(query)

        return result.scalar() or 0
