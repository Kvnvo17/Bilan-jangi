"""
SQLAlchemy Async — PostgreSQL ulanishi.
"""
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


# Render/Heroku ba'zan "postgres://" beradi — asyncpg buni tushunmaydi,
# shuning uchun avtomatik to'g'rilaymiz.
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
elif db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(db_url, echo=False, pool_pre_ping=True, pool_size=5, max_overflow=10)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def init_models() -> None:
    """Ilova ishga tushganda jadvallarni yaratadi (birinchi bosqich uchun,
    keyinchalik Alembic migratsiyalariga o'tish tavsiya etiladi)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await run_lightweight_migrations()


# Alembic o'rniga: eski (allaqachon deploy qilingan) bazalarga yangi
# ustunlarni xavfsiz qo'shib boradigan yengil migratsiya ro'yxati.
# create_all() faqat YO'Q jadvallarni yaratadi, mavjud jadvalga yangi ustun
# qo'shmaydi — shuning uchun bu funksiya har bosqichda kengaytiriladi.
_LIGHTWEIGHT_MIGRATIONS: list[str] = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS wins_1v1 INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS duels_played_1v1 INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS mass_duel_score INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS turnir_wins INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS premium_tier INTEGER DEFAULT 0",
    "ALTER TABLE daily_missions ADD COLUMN IF NOT EXISTS trigger_event VARCHAR(32)",
    "ALTER TABLE monthly_missions ADD COLUMN IF NOT EXISTS trigger_event VARCHAR(32)",
]


async def run_lightweight_migrations() -> None:
    from sqlalchemy import text

    async with engine.begin() as conn:
        for statement in _LIGHTWEIGHT_MIGRATIONS:
            try:
                await conn.execute(text(statement))
            except Exception:
                # Eski PostgreSQL versiyalarida "IF NOT EXISTS" har doim
                # qo'llab-quvvatlanmasligi mumkin — xavfsiz o'tkazib yuboramiz.
                pass
