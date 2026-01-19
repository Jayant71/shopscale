from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import config

Base = declarative_base()
DATABASE_URL = config.database_url

if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
    )
sessionLocal = AsyncSession(autocommit=False, autoflush=False, bind=engine)


async def get_db():
    async with sessionLocal as db:
        try:
            yield db
        finally:
            await db.close()
