from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/tournament", tags=["tournament"])


async def _to_out(db: AsyncSession, t) -> schemas.TournamentOut:
    owner = await crud.get_user_by_id(db, t.owner_id) if t.owner_id else None
    count = await crud.tournament_participant_count(db, t.id)
    return schemas.TournamentOut(
        code=t.code, name=t.name,
        owner=schemas.UserBrief.model_validate(owner) if owner else None,
        is_admin_tournament=t.is_admin_tournament,
        max_participants=t.max_participants,
        participant_count=count,
        prize_text=t.prize_text,
        total_questions=t.total_questions,
        status=t.status,
    )


@router.get("/list", response_model=schemas.TournamentListOut)
async def list_tournaments(db: AsyncSession = Depends(get_db)):
    tournaments = await crud.list_open_tournaments(db)
    return schemas.TournamentListOut(tournaments=[await _to_out(db, t) for t in tournaments])


@router.post("/create", response_model=schemas.TournamentOut)
async def create_tournament(payload: schemas.TournamentCreateRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    t, message = await crud.create_tournament(
        db, user, payload.name, payload.is_admin_tournament, payload.prize_text, payload.total_questions
    )
    if t is None:
        raise HTTPException(status_code=400, detail=message)
    return await _to_out(db, t)


@router.post("/join", response_model=schemas.TournamentOut)
async def join_tournament(payload: schemas.TournamentJoinRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    t, message = await crud.join_tournament(db, user, payload.code)
    if t is None:
        raise HTTPException(status_code=400, detail=message)
    return await _to_out(db, t)


@router.get("/{code}", response_model=schemas.TournamentDetailOut)
async def get_tournament(code: str, telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    t = await crud.get_tournament_by_code(db, code)
    if t is None:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")

    rows = await crud.get_tournament_leaderboard(db, t)
    leaderboard = [
        schemas.TournamentLeaderboardEntry(rank=i + 1, user=schemas.UserBrief.model_validate(u), score=p.score)
        for i, (p, u) in enumerate(rows)
    ]
    participant = await crud.get_tournament_participant(db, t, user)
    return schemas.TournamentDetailOut(
        tournament=await _to_out(db, t),
        leaderboard=leaderboard,
        my_current_index=participant.current_index if participant else 0,
        my_score=participant.score if participant else 0,
    )


@router.get("/{code}/question", response_model=schemas.QuestionOut | None)
async def get_current_question(code: str, telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    t = await crud.get_tournament_by_code(db, code)
    if t is None:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")
    participant = await crud.get_tournament_participant(db, t, user)
    if participant is None:
        raise HTTPException(status_code=400, detail="Avval turnirga qo'shiling")

    q_ids = crud._tournament_question_ids(t)
    if participant.current_index >= len(q_ids):
        return None
    from sqlalchemy import select

    result = await db.execute(select(models.Question).where(models.Question.id == q_ids[participant.current_index]))
    question = result.scalar_one_or_none()
    return schemas.QuestionOut.model_validate(question) if question else None


@router.post("/answer", response_model=schemas.TournamentAnswerResult)
async def answer(payload: schemas.TournamentAnswerRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    t = await crud.get_tournament_by_code(db, payload.code)
    if t is None:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")
    result, message = await crud.submit_tournament_answer(db, user, t, payload.question_id, payload.selected_option)
    if result is None:
        raise HTTPException(status_code=400, detail=message)
    return schemas.TournamentAnswerResult(**result)


@router.post("/close")
async def close_tournament(payload: schemas.TournamentJoinRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    t = await crud.get_tournament_by_code(db, payload.code)
    if t is None:
        raise HTTPException(status_code=404, detail="Turnir topilmadi")
    ok, message = await crud.close_tournament(db, user, t)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}
