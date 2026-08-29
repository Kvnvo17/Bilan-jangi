from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/mass-duel", tags=["mass-duel"])


async def _to_out(db: AsyncSession, duel) -> schemas.MassDuelOut:
    owner = await crud.get_user_by_id(db, duel.owner_id) if duel.owner_id else None
    count = await crud.mass_duel_participant_count(db, duel.id)
    return schemas.MassDuelOut(
        code=duel.code,
        name=duel.name,
        owner=schemas.UserBrief.model_validate(owner) if owner else None,
        is_admin_duel=duel.is_admin_duel,
        max_participants=duel.max_participants,
        participant_count=count,
        status=duel.status,
        fund=float(duel.fund),
    )


@router.get("/list", response_model=schemas.MassDuelListOut)
async def list_duels(db: AsyncSession = Depends(get_db)):
    duels = await crud.list_open_mass_duels(db)
    return schemas.MassDuelListOut(duels=[await _to_out(db, d) for d in duels])


@router.post("/create", response_model=schemas.MassDuelOut)
async def create_duel(payload: schemas.MassDuelCreateRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel, message = await crud.create_mass_duel(db, user, payload.name, payload.is_admin_duel, payload.option_count)
    if duel is None:
        raise HTTPException(status_code=400, detail=message)
    return await _to_out(db, duel)


@router.post("/join", response_model=schemas.MassDuelOut)
async def join_duel(payload: schemas.MassDuelJoinRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel, message = await crud.join_mass_duel(db, user, payload.code)
    if duel is None:
        raise HTTPException(status_code=400, detail=message)
    return await _to_out(db, duel)


@router.get("/{code}", response_model=schemas.MassDuelDetailOut)
async def get_duel(code: str, db: AsyncSession = Depends(get_db)):
    duel = await crud.get_mass_duel_by_code(db, code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")
    await crud.maybe_auto_close_mass_duel(db, duel)
    rows = await crud.get_mass_duel_leaderboard(db, duel)
    leaderboard = [
        schemas.MassDuelLeaderboardEntry(user=schemas.UserBrief.model_validate(u), score=p.score) for p, u in rows
    ]
    return schemas.MassDuelDetailOut(duel=await _to_out(db, duel), leaderboard=leaderboard)


@router.post("/question/add", response_model=schemas.MassDuelQuestionOut)
async def add_question(payload: schemas.MassDuelQuestionCreateRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel = await crud.get_mass_duel_by_code(db, payload.code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")
    q, message = await crud.add_mass_duel_question(
        db, user, duel, payload.text, payload.option_a, payload.option_b, payload.option_c, payload.option_d, payload.correct_option
    )
    if q is None:
        raise HTTPException(status_code=400, detail=message)
    return schemas.MassDuelQuestionOut.model_validate(q)


@router.get("/{code}/next-question", response_model=schemas.MassDuelQuestionOut | None)
async def next_question(code: str, telegram_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=telegram_id)
    duel = await crud.get_mass_duel_by_code(db, code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")
    q = await crud.get_next_mass_duel_question(db, user, duel)
    if q is None:
        return None
    return schemas.MassDuelQuestionOut.model_validate(q)


@router.post("/answer", response_model=schemas.MassDuelAnswerResult)
async def answer(payload: schemas.MassDuelAnswerRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel = await crud.get_mass_duel_by_code(db, payload.code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")
    result, message = await crud.submit_mass_duel_answer(db, user, duel, payload.question_id, payload.selected_option)
    if result is None:
        raise HTTPException(status_code=400, detail=message)
    return schemas.MassDuelAnswerResult(**result)


@router.post("/close")
async def close_duel(payload: schemas.MassDuelCloseRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel = await crud.get_mass_duel_by_code(db, payload.code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")
    ok, message = await crud.close_mass_duel(db, user, duel)
    if not ok:
        raise HTTPException(status_code=400, detail=message)
    return {"detail": message}
