from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from src.config import settings


engine = create_async_engine(url=settings.DATABASE_URL_asyncpg, echo=True,)
async_session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False,)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session