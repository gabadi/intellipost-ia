"""
Database configuration and setup.

This module provides database connection management and base model setup
for the IntelliPost AI backend using async SQLAlchemy with PostgreSQL.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from infrastructure.config.settings import settings


class Base(DeclarativeBase):
    """SQLAlchemy declarative base with type annotations."""

    pass


# Create the async engine
engine = create_async_engine(
    settings.get_database_url(),
    echo=settings.debug,  # Log SQL queries in debug mode
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_timeout=settings.database_pool_timeout,
    pool_recycle=settings.database_pool_recycle,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_database_session() -> AsyncGenerator[AsyncSession]:
    """
    Get an async database session.

    This is a dependency function for FastAPI that provides
    a database session to route handlers.

    Yields:
        AsyncSession: An async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_database_tables():
    """
    Create all database tables.

    This function should be called during application startup
    to ensure all tables exist. In production, use Alembic migrations instead.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_database_connection():
    """
    Close the database connection.

    Call this during application shutdown to properly close
    all database connections.
    """
    await engine.dispose()
