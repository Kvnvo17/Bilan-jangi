from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/api/duel/bot", tags=["duel-bot"])


@router.get("/question", response_model=schemas.QuestionOut)
async def get_question(db: AsyncSession = Depends(get_db)):
    question = await crud.get_random_question(db)
    if question is None:
        raise HTTPException(status_code=404, detail="Savollar bazasi bo'sh")
    return schemas.QuestionOut.model_validate(question)


@router.post("/answer", response_model=schemas.BotDuelAnswerResult)
async def answer_question(payload: schemas.BotDuelAnswerRequest, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    from app import models

    user = await crud.get_or_create_user(db, telegram_id=payload.telegram_id)
    q_result = await db.execute(
        select(models.Question).where(models.Question.id == payload.question_id)
    )
    question = q_result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status_code=404, detail="Savol topilmadi")

    is_correct, coin_change, leveled_up = await crud.apply_bot_duel_answer(
        db, user, question, payload.selected_option
    )

    # "20 ta savolga javob berish" kunlik missiyasi progressini oshiramiz
    await crud.increment_mission_progress(db, user, "answer_20_questions", amount=1)

    return schemas.BotDuelAnswerResult(
        is_correct=is_correct,
        correct_option=question.correct_option,
        coin_change=coin_change,
        new_b_coin=float(user.b_coin),
        new_level=user.level,
        leveled_up=leveled_up,
    )
