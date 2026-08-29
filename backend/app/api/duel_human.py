from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.database import get_db

router = APIRouter(prefix="/api/duel/human", tags=["duel-human"])


def _duel_to_state(duel, player1: models.User, player2: models.User | None, current_question=None) -> schemas.HumanDuelStateOut:
    return schemas.HumanDuelStateOut(
        invite_code=duel.invite_code,
        status=duel.status,
        player1=schemas.UserBrief.model_validate(player1),
        player2=schemas.UserBrief.model_validate(player2) if player2 else None,
        current_turn_telegram_id=(
            player1.telegram_id
            if crud.human_duel_current_turn_user_id(duel) == duel.player1_id
            else (player2.telegram_id if player2 and crud.human_duel_current_turn_user_id(duel) == duel.player2_id else None)
        ),
        total_questions=duel.total_questions,
        current_index=duel.current_index,
        player1_correct=duel.player1_correct,
        player2_correct=duel.player2_correct,
        winner_telegram_id=None,
        current_question=schemas.QuestionOut.model_validate(current_question) if current_question else None,
    )


@router.post("/create", response_model=schemas.HumanDuelStateOut)
async def create_duel(payload: schemas.HumanDuelCreateRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel, message = await crud.create_human_duel(db, user, payload.target)
    if duel is None:
        raise HTTPException(status_code=400, detail=message)

    player2 = await crud.get_user_by_id(db, duel.player2_id) if duel.player2_id else None
    current_q = await _get_current_question(db, duel)
    return _duel_to_state(duel, user, player2, current_q)


@router.post("/join", response_model=schemas.HumanDuelStateOut)
async def join_duel(payload: schemas.HumanDuelJoinRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel, message = await crud.join_human_duel(db, user, payload.invite_code)
    if duel is None:
        raise HTTPException(status_code=400, detail=message)

    player1 = await crud.get_user_by_id(db, duel.player1_id)
    player2 = await crud.get_user_by_id(db, duel.player2_id) if duel.player2_id else None
    current_q = await _get_current_question(db, duel)
    return _duel_to_state(duel, player1, player2, current_q)


@router.get("/state/{invite_code}", response_model=schemas.HumanDuelStateOut)
async def get_state(invite_code: str, telegram_id: int, db: AsyncSession = Depends(get_db)):
    duel = await crud.get_human_duel_by_code(db, invite_code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")

    player1 = await crud.get_user_by_id(db, duel.player1_id)
    player2 = await crud.get_user_by_id(db, duel.player2_id) if duel.player2_id else None
    current_q = await _get_current_question(db, duel)
    return _duel_to_state(duel, player1, player2, current_q)


@router.post("/answer", response_model=schemas.HumanDuelAnswerResult)
async def answer(payload: schemas.HumanDuelAnswerRequest, db: AsyncSession = Depends(get_db)):
    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    duel = await crud.get_human_duel_by_code(db, payload.invite_code)
    if duel is None:
        raise HTTPException(status_code=404, detail="Duel topilmadi")

    result, message = await crud.submit_human_duel_answer(db, user, duel, payload.question_id, payload.selected_option)
    if result is None:
        raise HTTPException(status_code=400, detail=message)
    return schemas.HumanDuelAnswerResult(**result)


async def _get_current_question(db: AsyncSession, duel):
    if duel.status != "active":
        return None
    q_ids = crud._human_duel_question_ids(duel)
    if duel.current_index >= len(q_ids):
        return None
    from sqlalchemy import select

    result = await db.execute(select(models.Question).where(models.Question.id == q_ids[duel.current_index]))
    return result.scalar_one_or_none()
