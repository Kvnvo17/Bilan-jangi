"""
Ilova birinchi marta ishga tushganda (yoki jadval bo'sh bo'lsa) savollar
banki va kunlik missiyalarni ma'lumotlar bazasiga yuklaydi.

database/questions_seed.py va database/missions_seed.py fayllaridan o'qiydi
(loyiha ildizidagi "database/" papka — backendga tegishli emas, chunki
savollar/missiyalar butun loyiha uchun umumiy ma'lumot hisoblanadi).
"""
import importlib.util
import logging
import sys
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models

logger = logging.getLogger("bilim_jangi.seed")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"


def _load_module(name: str, filename: str):
    filepath = DATABASE_DIR / filename
    spec = importlib.util.spec_from_file_location(name, filepath)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)  # type: ignore
    return module


async def seed_questions(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count(models.Question.id)))).scalar_one()
    if count > 0:
        return
    module = _load_module("questions_seed", "questions_seed.py")
    for q in module.QUESTIONS:
        db.add(models.Question(**q))
    await db.commit()
    logger.info("Savollar bazasiga %s ta savol yuklandi", len(module.QUESTIONS))


async def seed_daily_missions(db: AsyncSession) -> None:
    """Key bo'yicha upsert: mavjud bo'lmagan missiyalarni qo'shadi, mavjudlarga
    tegmaydi (admin panelda o'zgartirilgan reward/is_active saqlanib qoladi)."""
    module = _load_module("missions_seed", "missions_seed.py")
    result = await db.execute(select(models.DailyMission.key))
    existing_keys = {row[0] for row in result.all()}
    added = 0
    for m in module.DAILY_MISSIONS:
        if m["key"] not in existing_keys:
            db.add(models.DailyMission(**m))
            added += 1
    # Eski (1/2-bosqich) missiyalarga trigger_event moslashtirish (agar hali yo'q bo'lsa)
    legacy_map = {"invite_3_friends": ("invite_friend", 3), "answer_20_questions": ("correct_answer", 20)}
    for key, (event, _count) in legacy_map.items():
        legacy_result = await db.execute(
            select(models.DailyMission).where(models.DailyMission.key == key, models.DailyMission.trigger_event.is_(None))
        )
        legacy = legacy_result.scalar_one_or_none()
        if legacy:
            legacy.trigger_event = event
    await db.commit()
    if added:
        logger.info("Kunlik missiyalar yangilandi: %s ta yangi qo'shildi", added)


async def seed_monthly_missions(db: AsyncSession) -> None:
    module = _load_module("monthly_missions_seed", "monthly_missions_seed.py")
    result = await db.execute(select(models.MonthlyMission.key))
    existing_keys = {row[0] for row in result.all()}
    added = 0
    for m in module.MONTHLY_MISSIONS:
        if m["key"] not in existing_keys:
            db.add(models.MonthlyMission(**m))
            added += 1
    legacy_map = {
        "monthly_100_correct": "correct_answer",
        "monthly_10_friends": "invite_friend",
        "monthly_5_duels_won": "duel_win",
    }
    for key, event in legacy_map.items():
        legacy_result = await db.execute(
            select(models.MonthlyMission).where(
                models.MonthlyMission.key == key, models.MonthlyMission.trigger_event.is_(None)
            )
        )
        legacy = legacy_result.scalar_one_or_none()
        if legacy:
            legacy.trigger_event = event
    await db.commit()
    if added:
        logger.info("Oylik missiyalar yangilandi: %s ta yangi qo'shildi", added)


async def seed_products(db: AsyncSession) -> None:
    count = (await db.execute(select(func.count(models.Product.id)))).scalar_one()
    if count > 0:
        return
    module = _load_module("products_seed", "products_seed.py")
    for p in module.PREMIUM_TIERS:
        db.add(models.Product(**p))
    for p in module.VOUCHER_PLANS:
        db.add(models.Product(**p))
    await db.commit()
    logger.info(
        "Mahsulotlar yuklandi: %s Premium tarif, %s Vaucher reja",
        len(module.PREMIUM_TIERS), len(module.VOUCHER_PLANS),
    )


async def run_all_seeds(db: AsyncSession) -> None:
    await seed_questions(db)
    await seed_daily_missions(db)
    await seed_monthly_missions(db)
    await seed_products(db)
