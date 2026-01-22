from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from delivery_system.db.models.base_model import DbBaseModel


class ClientModel(DbBaseModel):
    """Client entity with a fixed home location."""
    
    __tablename__ = "clients"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False, doc="Text address representation")
    
    # Координаты нужны для Redash (рисовать точки на карте)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
