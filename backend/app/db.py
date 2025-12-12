from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator
from app.settings import settings
import redis.asyncio as redis

# Base for ORM models
Base = declarative_base()

# Database engine
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Redis connection
redis_client: redis.Redis = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    redis_client = redis.from_url(settings.redis_url)
    await redis_client.ping()
    return redis_client


async def close_redis():
    """Close Redis connection"""
    global redis_client
    if redis_client:
        await redis_client.close()


async def init_db():
    """Initialize database connection"""
    async with engine.begin() as conn:
        # Test connection
        await conn.execute(text("SELECT 1"))


async def close_db():
    """Close database connections"""
    await engine.dispose()
    await close_redis()