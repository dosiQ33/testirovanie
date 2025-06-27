from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from app.database.database import async_session_maker
from .database import engine


Base = declarative_base()


async def get_session_with_commit() -> AsyncGenerator[AsyncSession, None]:
    """Регистрируем все таблицы в схеме ext чтобы sqlamchemy знал о них."""
    async with engine.begin() as conn:
        # Using lambda to make a partial here to pass schema and only.
        await conn.run_sync(lambda engine: Base.metadata.reflect(engine, schema="ext"))
        await conn.run_sync(Base.metadata.create_all)

    """Асинхронная сессия с автоматическим коммитом."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_without_commit() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронная сессия без автоматического коммита."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
