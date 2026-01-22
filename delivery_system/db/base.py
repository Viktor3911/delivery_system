from sqlalchemy.orm import DeclarativeBase

from delivery_system.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
