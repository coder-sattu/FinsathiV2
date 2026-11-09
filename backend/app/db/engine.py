"""Async SQLAlchemy engine and session setup."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

# create async engine
engine = create_async_engine(settings.database_url, echo=False, future=True, pool_pre_ping=True)

# create async session maker
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db_session():
    # yield db session or None on connection error
    try:
        session = async_session_factory()
    except Exception:
        yield None
        return

    async with session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            try:
                if session.is_active:
                    await session.rollback()
            except Exception:
                pass
