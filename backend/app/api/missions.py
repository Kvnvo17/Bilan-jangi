from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/missions", tags=["missions"])


@router.get("/daily/{telegram_id}", response_model=list[schemas.DailyMissionOut])
async def get_daily_missions(telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    missions = await crud.get_today_daily_missions(db)

    out: list[schemas.DailyMissionOut] = []
    for mission in missions:
        progress = await crud.get_today_progress(db, user, mission)
        out.append(
            schemas.DailyMissionOut(
                key=mission.key,
                title=mission.title,
                description=mission.description,
                requirement_count=mission.requirement_count,
                reward_coin=float(mission.reward_coin),
                progress=progress.progress,
                completed=progress.completed,
                claimed=progress.claimed,
            )
        )
    return out


@router.post("/claim")
async def claim_mission(payload: schemas.ClaimMissionRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)

    m_result = await db.execute(select(models.DailyMission).where(models.DailyMission.key == payload.key))
    mission = m_result.scalar_one_or_none()
    if mission is None:
        raise HTTPException(status_code=404, detail="Missiya topilmadi")

    progress = await crud.get_today_progress(db, user, mission)
    if not progress.completed:
        raise HTTPException(status_code=400, detail="Missiya hali bajarilmagan")
    if progress.claimed:
        raise HTTPException(status_code=400, detail="Mukofot allaqachon olingan")

    progress.claimed = True
    user.b_coin = float(user.b_coin) + float(mission.reward_coin)
    await db.commit()
    await db.refresh(user)

    return {"reward_coin": float(mission.reward_coin), "new_b_coin": float(user.b_coin)}
