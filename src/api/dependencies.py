from typing import (
    AsyncGenerator
)
from sqlalchemy.ext.asyncio import (
    AsyncSession
)

from src.repository.database import async_db


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_db.async_session() as session:
        yield session
