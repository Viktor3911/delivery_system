from delivery_system.db.dao.base import BaseDAO
from delivery_system.db.models.order_model import OrderModel


class OrderDAO(BaseDAO):
    """DAO for Order models."""

    async def add(self, order: OrderModel) -> None:
        """Add single order."""
        self.session.add(order)
