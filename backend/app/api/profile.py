from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.post("/sync", response_model=schemas.ProfileOut)
async def sync_profile(payload: schemas.ProfileSyncRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(
        db,
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
        avatar_url=payload.avatar_url,
    )
    return schemas.ProfileOut(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        avatar_url=user.avatar_url,
        level=user.level,
        correct_answers_total=user.correct_answers_total,
        b_coin=float(user.b_coin),
        is_admin=user.is_admin,
    )


@router.get("/{telegram_id}", response_model=schemas.ProfileOut)
async def get_profile(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    return schemas.ProfileOut(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        avatar_url=user.avatar_url,
        level=user.level,
        correct_answers_total=user.correct_answers_total,
        b_coin=float(user.b_coin),
        is_admin=user.is_admin,
    )
