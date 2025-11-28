from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import settings


def _build_async_database_url() -> str:
    url = str(settings.build_database_url())
    if "+asyncpg" in url:
        return url
    if "+psycopg" in url:
        return url.replace("+psycopg", "+asyncpg")
    if "+psycopg2" in url:
        return url.replace("+psycopg2", "+asyncpg")
    if "postgresql://" in url and "+asyncpg" not in url:
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


engine = create_async_engine(_build_async_database_url(), pool_pre_ping=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный dependency, который предоставляет сессию БД и корректно закрывает её после использования."""
    async with SessionLocal() as session:
        yield session
