from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, Float, Enum, String, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from delivery_system.db.models.base_model import DbBaseModel
from delivery_system.db.models.enums import OrderStatus


class OrderModel(DbBaseModel):
    """Delivery order entity."""

    __tablename__ = "orders"

    # Связи
    client_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("clients.id"), nullable=False)
    courier_id: Mapped[UUID] = mapped_column(PGUUID, ForeignKey("couriers.id"), nullable=False)

    # Статус
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), 
        nullable=False, 
        default=OrderStatus.DELIVERED
    )

    # Откуда везем (ресторан/магазин)
    pickup_address: Mapped[str] = mapped_column(String(255), nullable=False)
    pickup_lat: Mapped[float] = mapped_column(Float, nullable=False)
    pickup_lon: Mapped[float] = mapped_column(Float, nullable=False)

    # Куда везем (копия координат клиента, но храним явно, чтобы история не менялась при переезде клиента)
    delivery_lat: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_lon: Mapped[float] = mapped_column(Float, nullable=False)

    # Аналитика
    distance_km: Mapped[float] = mapped_column(Float, nullable=False, doc="Calculated distance")
    price: Mapped[float] = mapped_column(Float, nullable=False, doc="Calculated price based on distance and transport")

    # Время завершения (для расчета скорости доставки)
    # Если статус CANCELLED, это время отмены
    finished_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # ORM Relationships (для удобства в коде, если понадобится)
    client = relationship("ClientModel")
    courier = relationship("CourierModel")
