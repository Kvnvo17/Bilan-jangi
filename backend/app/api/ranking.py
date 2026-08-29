from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/ranking", tags=["ranking"])

VALID_TYPES = {"umumiy", "1v1", "turnir"}


@router.get("/{ranking_type}", response_model=list[schemas.RankingEntry])
async def get_ranking(ranking_type: str, db: AsyncSession = Depends(get_db)):
    if ranking_type not in VALID_TYPES:
        raise HTTPException(status_code=400, detail="Noto'g'ri reyting turi")
    users, scores = await crud.get_ranking(db, ranking_type)
    return [
        schemas.RankingEntry(rank=i + 1, user=schemas.UserBrief.model_validate(u), score=s)
        for i, (u, s) in enumerate(zip(users, scores))
    ]
