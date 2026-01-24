from sqlalchemy import select, func

from delivery_system.db.dao.base import BaseDAO
from delivery_system.db.models.courier_model import CourierModel


class CourierDAO(BaseDAO):
    """DAO for Courier models."""

    async def add_bulk(self, couriers: list[CourierModel]) -> None:
        """Efficiently add multiple couriers."""
        self.session.add_all(couriers)
        await self.session.flush()

    async def get_all_ids(self) -> list:
        """Get all courier IDs and their transport type."""
        query = select(CourierModel.id, CourierModel.transport_type)
        result = await self.session.execute(query)
        return result.all()

    async def get_count(self) -> int:
        """Count total couriers."""
        query = select(func.count()).select_from(CourierModel)
        result = await self.session.execute(query)
        return result.scalar() or 0
