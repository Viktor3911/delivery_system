from sqlalchemy.ext.asyncio import AsyncSession

class BaseDAO:
    """Base DAO class."""

    def __init__(self, session: AsyncSession):
        self.session = session
