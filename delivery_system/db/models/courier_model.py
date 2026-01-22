from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped, mapped_column

from delivery_system.db.models.base_model import DbBaseModel
from delivery_system.db.models.enums import TransportType


class CourierModel(DbBaseModel):
    """Courier entity."""

    __tablename__ = "couriers"

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    transport_type: Mapped[TransportType] = mapped_column(
        Enum(TransportType), 
        nullable=False,
        default=TransportType.FOOT
    )
