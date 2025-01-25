from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
from src.config import app_config


class AsyncDatabase:
    def __init__(self) -> None:
        IS_SQLITE = app_config.DATABASE_URL.startswith('sqlite')
        
        if IS_SQLITE:
            self.async_engine: AsyncEngine = create_async_engine(
                url=app_config.DATABASE_URL,
                echo=app_config.SQL_DEBUG,
                connect_args={"check_same_thread": False}
            )
        else:
            self.async_engine: AsyncEngine = create_async_engine(
                url=app_config.DATABASE_URL,
                echo=app_config.SQL_DEBUG,
                pool_size=app_config.DB_POOL_SIZE,
                max_overflow=app_config.DB_POOL_OVERFLOW,
                pool_timeout=app_config.DB_TIMEOUT,
                poolclass=AsyncAdaptedQueuePool
            )
        
        self.async_session = async_sessionmaker(
            self.async_engine, class_=AsyncSession,
            autoflush=False, autocommit=False)


async_db = AsyncDatabase()
