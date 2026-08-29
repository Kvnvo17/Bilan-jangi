"""
SQLAlchemy Async — SQLite ulanishi.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
from app.config import settings


class Base(DeclarativeBase):
    pass


db_url = settings.DATABASE_URL

engine = create_async_engine(
    db_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


_LIGHTWEIGHT_MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN wins_1v1 INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN duels_played_1v1 INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN mass_duel_score INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN turnir_wins INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN premium_tier INTEGER DEFAULT 0",
    "ALTER TABLE daily_missions ADD COLUMN trigger_event VARCHAR(32)",
    "ALTER TABLE monthly_missions ADD COLUMN trigger_event VARCHAR(32)",
]


async def run_lightweight_migrations():
    async with engine.begin() as conn:
        for stmt in _LIGHTWEIGHT_MIGRATIONS:
            try:
                await conn.execute(text(stmt))
            except Exception:
                pass


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await run_lightweight_migrations()
