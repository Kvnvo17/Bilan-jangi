import random
import string
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import settings

LEVEL_UP_EVERY_CORRECT = 99  # har 99 ta to'g'ri javob = +1 level


def generate_code(length: int = 6) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    return await db.get(models.User, user_id)


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> models.User | None:
    result = await db.execute(select(models.User).where(models.User.username == username.lstrip("@")))
    return result.scalar_one_or_none()


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    username: str | None = None,
    first_name: str = "",
    avatar_url: str | None = None,
) -> models.User:
    result = await db.execute(select(models.User).where(models.User.telegram_id == telegram_id))
    user = result.scalar_one_or_none()
    is_admin_by_config = bool(settings.ADMIN_TELEGRAM_ID) and telegram_id == settings.ADMIN_TELEGRAM_ID
    if user is None:
        user = models.User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name or "",
            avatar_url=avatar_url,
            is_admin=is_admin_by_config,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        if is_admin_by_config and not user.is_admin:
            user.is_admin = True
            await db.commit()
        changed = False
        if username and user.username != username:
            user.username = username
            changed = True
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            changed = True
        if changed:
            await db.commit()
            await db.refresh(user)
    return user


async def get_random_question(db: AsyncSession) -> models.Question | None:
    result = await db.execute(
        select(models.Question)
        .where(models.Question.is_active == True)  # noqa: E712
        .order_by(models.Question.id)
    )
    all_q = result.scalars().all()
    if not all_q:
        return None
    import random

    return random.choice(all_q)


async def apply_bot_duel_answer(
    db: AsyncSession, user: models.User, question: models.Question, selected_option: str
) -> tuple[bool, float, bool]:
    """To'g'ri: +0.50 B Coin, har 99 ta to'g'ri javob = +1 Level."""
    is_correct = selected_option.upper() == question.correct_option.upper()
    coin_change = 0.50 if is_correct else 0.0
    leveled_up = False

    if is_correct:
        user.correct_answers_total += 1
        user.b_coin = float(user.b_coin) + coin_change
        if user.correct_answers_total % LEVEL_UP_EVERY_CORRECT == 0:
            user.level += 1
            leveled_up = True

    db.add(
        models.BotDuelLog(
            user_id=user.id,
            question_id=question.id,
            is_correct=is_correct,
            coin_change=coin_change,
        )
    )
    await db.commit()
    await db.refresh(user)
    if is_correct:
        await dispatch_mission_event(db, user, "correct_answer")
    return is_correct, coin_change, leveled_up


async def get_active_daily_missions(db: AsyncSession) -> list[models.DailyMission]:
    result = await db.execute(
        select(models.DailyMission).where(models.DailyMission.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())


async def get_today_progress(
    db: AsyncSession, user: models.User, mission: models.DailyMission
) -> models.UserDailyMissionProgress:
    today = date.today()
    result = await db.execute(
        select(models.UserDailyMissionProgress).where(
            models.UserDailyMissionProgress.user_id == user.id,
            models.UserDailyMissionProgress.mission_id == mission.id,
            models.UserDailyMissionProgress.mission_date == today,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        progress = models.UserDailyMissionProgress(
            user_id=user.id, mission_id=mission.id, mission_date=today
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    return progress


async def increment_mission_progress(
    db: AsyncSession, user: models.User, mission_key: str, amount: int = 1
) -> None:
    """Foydalanuvchi harakati (masalan savolga javob berdi) bo'yicha
    tegishli kunlik missiya progressini oshiradi."""
    result = await db.execute(
        select(models.DailyMission).where(
            models.DailyMission.key == mission_key, models.DailyMission.is_active == True  # noqa: E712
        )
    )
    mission = result.scalar_one_or_none()
    if mission is None:
        return
    progress = await get_today_progress(db, user, mission)
    if progress.completed:
        return
    progress.progress += amount
    if progress.progress >= mission.requirement_count:
        progress.completed = True
    await db.commit()


# ============================================================
# 2-bosqich: Do'stlar
# ============================================================

async def resolve_user_by_target(db: AsyncSession, target: str) -> "models.User | None":
    """target — username (@ bilan/siz) yoki telegram_id raqami bo'lishi mumkin."""
    target = target.strip()
    if target.startswith("@"):
        target = target[1:]
    if target.isdigit():
        user = await get_user_by_telegram_id(db, int(target))
        if user:
            return user
    return await get_user_by_username(db, target)


async def search_users(db: AsyncSession, query: str, exclude_telegram_id: int, limit: int = 20) -> list["models.User"]:
    like = f"%{query.lstrip('@')}%"
    result = await db.execute(
        select(models.User)
        .where(
            models.User.telegram_id != exclude_telegram_id,
            (models.User.username.ilike(like)) | (models.User.first_name.ilike(like)),
        )
        .limit(limit)
    )
    return list(result.scalars().all())


async def send_friend_request(db: AsyncSession, from_user: "models.User", target: str) -> tuple[bool, str]:
    to_user = await resolve_user_by_target(db, target)
    if to_user is None:
        return False, "Foydalanuvchi topilmadi"
    if to_user.id == from_user.id:
        return False, "O'zingizga so'rov yubora olmaysiz"

    existing = await db.execute(
        select(models.FriendRequest).where(
            (
                (models.FriendRequest.from_user_id == from_user.id)
                & (models.FriendRequest.to_user_id == to_user.id)
            )
            | (
                (models.FriendRequest.from_user_id == to_user.id)
                & (models.FriendRequest.to_user_id == from_user.id)
            )
        )
    )
    existing_req = existing.scalars().first()
    if existing_req and existing_req.status == "accepted":
        return False, "Siz allaqachon do'stsiz"
    if existing_req and existing_req.status == "pending":
        return False, "So'rov allaqachon yuborilgan"

    db.add(models.FriendRequest(from_user_id=from_user.id, to_user_id=to_user.id, status="pending"))
    await db.commit()
    return True, "So'rov yuborildi"


async def respond_friend_request(db: AsyncSession, user: "models.User", request_id: int, action: str) -> tuple[bool, str]:
    req = await db.get(models.FriendRequest, request_id)
    if req is None or req.to_user_id != user.id:
        return False, "So'rov topilmadi"
    if req.status != "pending":
        return False, "So'rov allaqachon ko'rib chiqilgan"
    req.status = "accepted" if action == "accept" else "rejected"
    await db.commit()
    if action == "accept":
        inviter = await get_user_by_id(db, req.from_user_id)
        if inviter:
            await dispatch_mission_event(db, inviter, "invite_friend")
    return True, "Bajarildi"


async def get_friends_list(db: AsyncSession, user: "models.User") -> list["models.User"]:
    result = await db.execute(
        select(models.FriendRequest).where(
            models.FriendRequest.status == "accepted",
            (models.FriendRequest.from_user_id == user.id) | (models.FriendRequest.to_user_id == user.id),
        )
    )
    friend_ids = set()
    for req in result.scalars().all():
        friend_ids.add(req.to_user_id if req.from_user_id == user.id else req.from_user_id)
    if not friend_ids:
        return []
    result = await db.execute(select(models.User).where(models.User.id.in_(friend_ids)))
    return list(result.scalars().all())


async def get_incoming_requests(db: AsyncSession, user: "models.User"):
    result = await db.execute(
        select(models.FriendRequest, models.User)
        .join(models.User, models.User.id == models.FriendRequest.from_user_id)
        .where(models.FriendRequest.to_user_id == user.id, models.FriendRequest.status == "pending")
    )
    return result.all()


async def get_outgoing_requests(db: AsyncSession, user: "models.User"):
    result = await db.execute(
        select(models.FriendRequest, models.User)
        .join(models.User, models.User.id == models.FriendRequest.to_user_id)
        .where(models.FriendRequest.from_user_id == user.id, models.FriendRequest.status == "pending")
    )
    return result.all()


async def gift_coin(db: AsyncSession, from_user: "models.User", to_user: "models.User", amount: float) -> tuple[bool, str]:
    if float(from_user.b_coin) < amount:
        return False, "B Coin yetarli emas"
    from_user.b_coin = float(from_user.b_coin) - amount
    to_user.b_coin = float(to_user.b_coin) + amount
    await db.commit()
    await dispatch_mission_event(db, from_user, "gift_sent")
    return True, "Sovg'a yuborildi"


# ============================================================
# 2-bosqich: 👤 Odam bilan 1v1 Duel
# ============================================================

async def pick_random_question_ids(db: AsyncSession, count: int) -> list[int]:
    result = await db.execute(select(models.Question.id).where(models.Question.is_active == True))  # noqa: E712
    ids = [row[0] for row in result.all()]
    random.shuffle(ids)
    return ids[:count] if len(ids) >= count else ids


async def create_human_duel(db: AsyncSession, player1: "models.User", target: str | None):
    total_questions = 10
    question_ids = await pick_random_question_ids(db, total_questions)
    if not question_ids:
        return None, "Savollar bazasi bo'sh"

    player2 = None
    if target:
        player2 = await resolve_user_by_target(db, target)
        if player2 and player2.id == player1.id:
            return None, "O'zingizga duel taklif qila olmaysiz"

    code = generate_code(8)
    duel = models.HumanDuel(
        invite_code=code,
        player1_id=player1.id,
        player2_id=player2.id if player2 else None,
        status="active" if player2 else "waiting_for_opponent",
        question_ids=",".join(str(i) for i in question_ids),
        total_questions=len(question_ids),
    )
    db.add(duel)
    await db.commit()
    await db.refresh(duel)
    return duel, "OK"


async def join_human_duel(db: AsyncSession, user: "models.User", invite_code: str):
    result = await db.execute(select(models.HumanDuel).where(models.HumanDuel.invite_code == invite_code))
    duel = result.scalar_one_or_none()
    if duel is None:
        return None, "Duel topilmadi"
    if duel.player1_id == user.id:
        return duel, "OK"
    if duel.player2_id and duel.player2_id != user.id:
        return None, "Bu duelda ikkinchi o'yinchi allaqachon band"
    if duel.status not in ("waiting_for_opponent", "active"):
        return None, "Duel tugagan"
    if not duel.player2_id:
        duel.player2_id = user.id
        duel.status = "active"
        await db.commit()
        await db.refresh(duel)
    return duel, "OK"


async def get_human_duel_by_code(db: AsyncSession, invite_code: str):
    result = await db.execute(select(models.HumanDuel).where(models.HumanDuel.invite_code == invite_code))
    return result.scalar_one_or_none()


def _human_duel_question_ids(duel) -> list[int]:
    return [int(x) for x in duel.question_ids.split(",") if x]


def human_duel_current_turn_user_id(duel) -> int | None:
    if duel.status != "active" or not duel.player2_id:
        return None
    # navbat: juft indeks -> player1, toq indeks -> player2
    return duel.player1_id if duel.current_index % 2 == 0 else duel.player2_id


async def submit_human_duel_answer(
    db: AsyncSession, user: "models.User", duel, question_id: int, selected_option: str
):
    if duel.status != "active":
        return None, "Duel faol emas"
    turn_user_id = human_duel_current_turn_user_id(duel)
    if turn_user_id != user.id:
        return None, "Bu sizning navbatingiz emas"

    q_ids = _human_duel_question_ids(duel)
    if duel.current_index >= len(q_ids) or q_ids[duel.current_index] != question_id:
        return None, "Bu savol navbatdagi savol emas"

    q_result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = q_result.scalar_one_or_none()
    if question is None:
        return None, "Savol topilmadi"

    is_correct = selected_option.upper() == question.correct_option.upper()
    coin_change = 1.0 if is_correct else 0.0
    if is_correct:
        user.b_coin = float(user.b_coin) + coin_change
        if user.id == duel.player1_id:
            duel.player1_correct += 1
        else:
            duel.player2_correct += 1
    duel.current_index += 1
    duel_finished = duel.current_index >= duel.total_questions
    winner_telegram_id = None

    if duel_finished:
        duel.status = "finished"
        p1 = await get_user_by_id(db, duel.player1_id)
        p2 = await get_user_by_id(db, duel.player2_id)
        p1.duels_played_1v1 += 1
        p2.duels_played_1v1 += 1
        if duel.player1_correct > duel.player2_correct:
            duel.winner_id = duel.player1_id
            p1.wins_1v1 += 1
            winner_telegram_id = p1.telegram_id
        elif duel.player2_correct > duel.player1_correct:
            duel.winner_id = duel.player2_id
            p2.wins_1v1 += 1
            winner_telegram_id = p2.telegram_id
        # teng bo'lsa g'olib yo'q (durang)

    await db.commit()
    await db.refresh(duel)
    if is_correct:
        await dispatch_mission_event(db, user, "correct_answer")
    if duel_finished:
        await dispatch_mission_event(db, p1, "human_duel_played")
        await dispatch_mission_event(db, p2, "human_duel_played")
        if winner_telegram_id:
            winner = await get_user_by_telegram_id(db, winner_telegram_id)
            if winner:
                await dispatch_mission_event(db, winner, "duel_win")
    return {
        "is_correct": is_correct,
        "correct_option": question.correct_option,
        "coin_change": coin_change,
        "duel_finished": duel_finished,
        "winner_telegram_id": winner_telegram_id,
    }, "OK"


# ============================================================
# 2-bosqich: 🌍 Ommaviy Duel
# ============================================================

MASS_DUEL_INACTIVITY_MINUTES = 10


async def create_mass_duel(db: AsyncSession, owner: "models.User", name: str, is_admin_duel: bool, option_count: int):
    if is_admin_duel and not owner.is_admin:
        return None, "Faqat admin admin-duel yarata oladi"
    code = generate_code(6)
    duel = models.MassDuel(
        code=code,
        name=name.strip()[:128] or "Ommaviy Duel",
        owner_id=owner.id,
        is_admin_duel=is_admin_duel,
        max_participants=100 if is_admin_duel else 50,
        option_count=4 if option_count not in (3, 4) else option_count,
        status="open",
    )
    db.add(duel)
    await db.flush()
    db.add(models.MassDuelParticipant(duel_id=duel.id, user_id=owner.id))
    await db.commit()
    await db.refresh(duel)
    return duel, "OK"


async def get_mass_duel_by_code(db: AsyncSession, code: str):
    result = await db.execute(select(models.MassDuel).where(models.MassDuel.code == code))
    return result.scalar_one_or_none()


async def maybe_auto_close_mass_duel(db: AsyncSession, duel) -> None:
    if duel.status != "open" or not duel.last_question_at:
        return
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    last = duel.last_question_at
    if last.tzinfo is None:
        last = last.replace(tzinfo=timezone.utc)
    if (now - last).total_seconds() > MASS_DUEL_INACTIVITY_MINUTES * 60:
        await close_mass_duel_internal(db, duel)


async def join_mass_duel(db: AsyncSession, user: "models.User", code: str):
    duel = await get_mass_duel_by_code(db, code)
    if duel is None:
        return None, "Duel topilmadi"
    await maybe_auto_close_mass_duel(db, duel)
    if duel.status != "open":
        return None, "Duel yopilgan"

    result = await db.execute(
        select(models.MassDuelParticipant).where(
            models.MassDuelParticipant.duel_id == duel.id, models.MassDuelParticipant.user_id == user.id
        )
    )
    if result.scalar_one_or_none():
        return duel, "OK"

    count_result = await db.execute(
        select(func.count(models.MassDuelParticipant.id)).where(models.MassDuelParticipant.duel_id == duel.id)
    )
    count = count_result.scalar_one()
    if count >= duel.max_participants:
        return None, "Duel to'lgan"

    db.add(models.MassDuelParticipant(duel_id=duel.id, user_id=user.id))
    await db.commit()
    await dispatch_mission_event(db, user, "mass_duel_played")
    return duel, "OK"


async def add_mass_duel_question(
    db: AsyncSession, user: "models.User", duel, text: str, a: str, b: str, c: str, d: str | None, correct: str
):
    from datetime import datetime, timezone

    if duel.status != "open":
        return None, "Duel yopilgan"
    q = models.MassDuelQuestion(
        duel_id=duel.id,
        owner_user_id=user.id,
        text=text.strip(),
        option_a=a, option_b=b, option_c=c, option_d=d,
        correct_option=correct.upper(),
    )
    db.add(q)
    duel.last_question_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(q)
    return q, "OK"


async def get_next_mass_duel_question(db: AsyncSession, user: "models.User", duel):
    await maybe_auto_close_mass_duel(db, duel)

    answered_result = await db.execute(
        select(models.MassDuelAnswer.question_id).where(
            models.MassDuelAnswer.duel_id == duel.id, models.MassDuelAnswer.user_id == user.id
        )
    )
    answered_ids = {row[0] for row in answered_result.all()}

    result = await db.execute(
        select(models.MassDuelQuestion).where(
            models.MassDuelQuestion.duel_id == duel.id,
            models.MassDuelQuestion.is_active == True,  # noqa: E712
            models.MassDuelQuestion.owner_user_id != user.id,
        )
    )
    candidates = [q for q in result.scalars().all() if q.id not in answered_ids]
    if not candidates:
        return None
    return random.choice(candidates)


async def submit_mass_duel_answer(db: AsyncSession, user: "models.User", duel, question_id: int, selected_option: str):
    if duel.status != "open":
        return None, "Duel yopilgan"

    q_result = await db.execute(select(models.MassDuelQuestion).where(models.MassDuelQuestion.id == question_id))
    question = q_result.scalar_one_or_none()
    if question is None or question.duel_id != duel.id:
        return None, "Savol topilmadi"
    if question.owner_user_id == user.id:
        return None, "O'z savolingizga javob bera olmaysiz"

    existing = await db.execute(
        select(models.MassDuelAnswer).where(
            models.MassDuelAnswer.duel_id == duel.id,
            models.MassDuelAnswer.user_id == user.id,
            models.MassDuelAnswer.question_id == question_id,
        )
    )
    if existing.scalar_one_or_none():
        return None, "Bu savolga allaqachon javob bergansiz"

    is_correct = selected_option.upper() == question.correct_option.upper()

    if duel.is_admin_duel:
        if is_correct:
            coin_change = 1.0
            user.b_coin = float(user.b_coin) + coin_change
        else:
            coin_change = -0.10
            penalty = 0.10
            user.b_coin = max(0.0, float(user.b_coin) - penalty)
            if duel.owner_id:
                owner = await get_user_by_id(db, duel.owner_id)
                if owner:
                    owner.b_coin = float(owner.b_coin) + penalty
            duel.fund = float(duel.fund) + penalty
    else:
        if is_correct:
            coin_change = 0.80
            user.b_coin = float(user.b_coin) + coin_change
        else:
            coin_change = -0.20
            penalty = 0.20
            user.b_coin = max(0.0, float(user.b_coin) - penalty)
            if question.owner_user_id:
                q_owner = await get_user_by_id(db, question.owner_user_id)
                if q_owner:
                    q_owner.b_coin = float(q_owner.b_coin) + penalty

    db.add(
        models.MassDuelAnswer(
            duel_id=duel.id, question_id=question_id, user_id=user.id, is_correct=is_correct, coin_change=coin_change
        )
    )

    if is_correct:
        p_result = await db.execute(
            select(models.MassDuelParticipant).where(
                models.MassDuelParticipant.duel_id == duel.id, models.MassDuelParticipant.user_id == user.id
            )
        )
        participant = p_result.scalar_one_or_none()
        if participant:
            participant.score += 1
        user.mass_duel_score += 1

    await db.commit()
    await db.refresh(user)
    if is_correct:
        await dispatch_mission_event(db, user, "correct_answer")
    return {
        "is_correct": is_correct,
        "correct_option": question.correct_option,
        "coin_change": coin_change,
        "new_b_coin": float(user.b_coin),
    }, "OK"


async def close_mass_duel_internal(db: AsyncSession, duel) -> None:
    from datetime import datetime, timezone

    if duel.status != "open":
        return
    duel.status = "closed"
    duel.closed_at = datetime.now(timezone.utc)

    if duel.is_admin_duel and float(duel.fund) > 0:
        result = await db.execute(
            select(models.MassDuelParticipant)
            .where(models.MassDuelParticipant.duel_id == duel.id)
            .order_by(models.MassDuelParticipant.score.desc())
            .limit(1)
        )
        top1 = result.scalar_one_or_none()
        if top1:
            bonus = float(duel.fund) * 0.5
            top_user = await get_user_by_id(db, top1.user_id)
            if top_user:
                top_user.b_coin = float(top_user.b_coin) + bonus
    await db.commit()


async def close_mass_duel(db: AsyncSession, user: "models.User", duel):
    if duel.owner_id != user.id and not user.is_admin:
        return False, "Faqat egasi yoki admin duelni yopa oladi"
    await close_mass_duel_internal(db, duel)
    return True, "Duel yopildi"


async def get_mass_duel_leaderboard(db: AsyncSession, duel):
    result = await db.execute(
        select(models.MassDuelParticipant, models.User)
        .join(models.User, models.User.id == models.MassDuelParticipant.user_id)
        .where(models.MassDuelParticipant.duel_id == duel.id)
        .order_by(models.MassDuelParticipant.score.desc())
    )
    return result.all()


async def list_open_mass_duels(db: AsyncSession, limit: int = 30):
    result = await db.execute(
        select(models.MassDuel)
        .where(models.MassDuel.status == "open")
        .order_by(models.MassDuel.is_admin_duel.desc(), models.MassDuel.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def mass_duel_participant_count(db: AsyncSession, duel_id: int) -> int:
    result = await db.execute(
        select(func.count(models.MassDuelParticipant.id)).where(models.MassDuelParticipant.duel_id == duel_id)
    )
    return result.scalar_one()


# ============================================================
# 2-bosqich: 🏆 Reyting
# ============================================================

async def get_ranking(db: AsyncSession, ranking_type: str, limit: int = 50):
    if ranking_type == "1v1":
        order_col = models.User.wins_1v1
    elif ranking_type == "turnir":
        order_col = models.User.turnir_wins
    else:
        order_col = models.User.correct_answers_total

    result = await db.execute(
        select(models.User).where(models.User.is_banned == False).order_by(order_col.desc()).limit(limit)  # noqa: E712
    )
    users = list(result.scalars().all())
    scores = []
    for u in users:
        if ranking_type == "1v1":
            scores.append(u.wins_1v1)
        elif ranking_type == "turnir":
            scores.append(u.turnir_wins)
        else:
            scores.append(u.correct_answers_total)
    return users, scores


# ============================================================
# 3-bosqich: 🏅 Turnir
# ============================================================

async def create_tournament(
    db: AsyncSession, owner: "models.User", name: str, is_admin_tournament: bool, prize_text: str, total_questions: int
):
    if is_admin_tournament and not owner.is_admin:
        return None, "Faqat admin admin-turnir yarata oladi"
    question_ids = await pick_random_question_ids(db, total_questions)
    if not question_ids:
        return None, "Savollar bazasi bo'sh"

    code = generate_code(6)
    tournament = models.Tournament(
        code=code,
        name=name.strip()[:128] or "Turnir",
        owner_id=owner.id,
        is_admin_tournament=is_admin_tournament,
        max_participants=200 if is_admin_tournament else 100,
        prize_text=prize_text.strip()[:512],
        question_ids=",".join(str(i) for i in question_ids),
        total_questions=len(question_ids),
    )
    db.add(tournament)
    await db.flush()
    db.add(models.TournamentParticipant(tournament_id=tournament.id, user_id=owner.id))
    await db.commit()
    await db.refresh(tournament)
    return tournament, "OK"


async def get_tournament_by_code(db: AsyncSession, code: str):
    result = await db.execute(select(models.Tournament).where(models.Tournament.code == code))
    return result.scalar_one_or_none()


async def join_tournament(db: AsyncSession, user: "models.User", code: str):
    tournament = await get_tournament_by_code(db, code)
    if tournament is None:
        return None, "Turnir topilmadi"
    if tournament.status != "open":
        return None, "Turnir yopilgan"

    result = await db.execute(
        select(models.TournamentParticipant).where(
            models.TournamentParticipant.tournament_id == tournament.id,
            models.TournamentParticipant.user_id == user.id,
        )
    )
    if result.scalar_one_or_none():
        return tournament, "OK"

    count_result = await db.execute(
        select(func.count(models.TournamentParticipant.id)).where(
            models.TournamentParticipant.tournament_id == tournament.id
        )
    )
    if count_result.scalar_one() >= tournament.max_participants:
        return None, "Turnir to'lgan"

    db.add(models.TournamentParticipant(tournament_id=tournament.id, user_id=user.id))
    await db.commit()
    await dispatch_mission_event(db, user, "tournament_played")
    return tournament, "OK"


async def get_tournament_participant(db: AsyncSession, tournament, user: "models.User"):
    result = await db.execute(
        select(models.TournamentParticipant).where(
            models.TournamentParticipant.tournament_id == tournament.id,
            models.TournamentParticipant.user_id == user.id,
        )
    )
    return result.scalar_one_or_none()


def _tournament_question_ids(tournament) -> list[int]:
    return [int(x) for x in tournament.question_ids.split(",") if x]


async def submit_tournament_answer(db: AsyncSession, user: "models.User", tournament, question_id: int, selected_option: str):
    if tournament.status != "open":
        return None, "Turnir yopilgan"
    participant = await get_tournament_participant(db, tournament, user)
    if participant is None:
        return None, "Avval turnirga qo'shiling"

    q_ids = _tournament_question_ids(tournament)
    if participant.current_index >= len(q_ids) or q_ids[participant.current_index] != question_id:
        return None, "Bu savol navbatdagi savol emas"

    q_result = await db.execute(select(models.Question).where(models.Question.id == question_id))
    question = q_result.scalar_one_or_none()
    if question is None:
        return None, "Savol topilmadi"

    is_correct = selected_option.upper() == question.correct_option.upper()

    if tournament.is_admin_tournament:
        correct_reward, wrong_penalty = 0.15, 0.35
    else:
        correct_reward, wrong_penalty = 0.10, 0.40

    if is_correct:
        coin_change = correct_reward
        user.b_coin = float(user.b_coin) + coin_change
        participant.score += 1
    else:
        coin_change = -wrong_penalty
        user.b_coin = max(0.0, float(user.b_coin) - wrong_penalty)
        beneficiary_id = None if tournament.is_admin_tournament else tournament.owner_id
        if tournament.is_admin_tournament:
            admin_result = await db.execute(select(models.User).where(models.User.is_admin == True))  # noqa: E712
            admin_user = admin_result.scalars().first()
            if admin_user:
                admin_user.b_coin = float(admin_user.b_coin) + wrong_penalty
        elif beneficiary_id:
            owner = await get_user_by_id(db, beneficiary_id)
            if owner:
                owner.b_coin = float(owner.b_coin) + wrong_penalty

    participant.current_index += 1
    finished_all = participant.current_index >= len(q_ids)

    db.add(
        models.TournamentAnswer(
            tournament_id=tournament.id, user_id=user.id, question_id=question_id,
            is_correct=is_correct, coin_change=coin_change,
        )
    )
    await db.commit()
    if is_correct:
        await dispatch_mission_event(db, user, "correct_answer")
    return {
        "is_correct": is_correct,
        "correct_option": question.correct_option,
        "coin_change": coin_change,
        "finished_all_questions": finished_all,
    }, "OK"


async def get_tournament_leaderboard(db: AsyncSession, tournament):
    result = await db.execute(
        select(models.TournamentParticipant, models.User)
        .join(models.User, models.User.id == models.TournamentParticipant.user_id)
        .where(models.TournamentParticipant.tournament_id == tournament.id)
        .order_by(models.TournamentParticipant.score.desc())
    )
    return result.all()


async def close_tournament(db: AsyncSession, user: "models.User", tournament):
    if tournament.owner_id != user.id and not user.is_admin:
        return False, "Faqat egasi yoki admin turnirni yopa oladi"
    if tournament.status != "open":
        return False, "Turnir allaqachon yopilgan"
    from datetime import datetime, timezone

    tournament.status = "closed"
    tournament.closed_at = datetime.now(timezone.utc)

    rows = await get_tournament_leaderboard(db, tournament)
    top_n = 3 if tournament.is_admin_tournament else 1
    for _, u in rows[:top_n]:
        u.turnir_wins += 1

    await db.commit()
    return True, "Turnir yopildi"


async def list_open_tournaments(db: AsyncSession, limit: int = 30):
    result = await db.execute(
        select(models.Tournament)
        .where(models.Tournament.status == "open")
        .order_by(models.Tournament.is_admin_tournament.desc(), models.Tournament.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def tournament_participant_count(db: AsyncSession, tournament_id: int) -> int:
    result = await db.execute(
        select(func.count(models.TournamentParticipant.id)).where(
            models.TournamentParticipant.tournament_id == tournament_id
        )
    )
    return result.scalar_one()


# ============================================================
# 3-bosqich: 🛒 Do'kon / 📦 Sklad / 👑 Premium / 🎟️ Vaucher
# ============================================================

SELLER_DAILY_LIMIT = 3


async def get_user_active_voucher(db: AsyncSession, user: "models.User"):
    from datetime import datetime, timezone

    result = await db.execute(
        select(models.UserVoucher)
        .where(models.UserVoucher.user_id == user.id, models.UserVoucher.is_active == True)  # noqa: E712
        .order_by(models.UserVoucher.expires_at.desc())
    )
    vouchers = result.scalars().all()
    now = datetime.now(timezone.utc)
    for v in vouchers:
        expires = v.expires_at if v.expires_at.tzinfo else v.expires_at.replace(tzinfo=timezone.utc)
        if expires > now:
            return v
        v.is_active = False
    if vouchers:
        await db.commit()
    return None


async def list_products(db: AsyncSession, catalog: str | None, user: "models.User | None" = None):
    stmt = select(models.Product).where(
        models.Product.is_active == True, models.Product.is_approved == True, models.Product.is_hidden == False  # noqa: E712
    )
    has_voucher = None  # lazy — faqat kerak bo'lsa tekshiramiz
    if catalog:
        stmt = stmt.where(models.Product.catalog == catalog)
        if catalog == "seller":
            if user is None or (await get_user_active_voucher(db, user)) is None:
                return []
    else:
        # "Hammasi" so'ralganda ham "seller" katalogini vaucher tekshiruvisiz chiqarib yubormaslik kerak
        if user is None:
            has_voucher = False
        else:
            has_voucher = (await get_user_active_voucher(db, user)) is not None
        if not has_voucher:
            stmt = stmt.where(models.Product.catalog != "seller")

    result = await db.execute(stmt.order_by(models.Product.created_at.desc()))
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: int):
    return await db.get(models.Product, product_id)


async def submit_seller_product(
    db: AsyncSession, user: "models.User", catalog: str, name: str, description: str, image_url: str | None, price_amount: float
):
    from datetime import datetime, timedelta, timezone

    if catalog not in ("seller", "frame", "nick_decor", "background", "badge"):
        return None, "Noto'g'ri katalog"

    # Mahsulot joylash — faqat faol vaucheri bor foydalanuvchilarga ruxsat
    # (Sotuvchilar ekotizimi: ko'rish, sotib olish va sotish — barchasi vaucher talab qiladi)
    voucher = await get_user_active_voucher(db, user)
    if voucher is None:
        return None, "Mahsulot joylash uchun faol Vaucher kerak"

    limits = {"badge": (500, 2000)}
    min_price, max_price = limits.get(catalog, (100, 1000))
    if not (min_price <= price_amount <= max_price):
        return None, f"Narx {min_price}-{max_price} oralig'ida bo'lishi kerak"

    since = datetime.now(timezone.utc) - timedelta(days=1)
    count_result = await db.execute(
        select(func.count(models.Product.id)).where(
            models.Product.seller_user_id == user.id, models.Product.created_at >= since
        )
    )
    if count_result.scalar_one() >= SELLER_DAILY_LIMIT:
        return None, f"Kuniga faqat {SELLER_DAILY_LIMIT} ta mahsulot joylash mumkin"

    product = models.Product(
        catalog=catalog,
        name=name.strip()[:128],
        description=description.strip()[:1024],
        image_url=image_url,
        price_type="coin",
        price_amount=price_amount,
        seller_user_id=user.id,
        is_approved=False,  # admin tasdig'ini kutadi
        is_active=True,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product, "Mahsulot admin tasdig'ini kutmoqda"


async def purchase_with_coin(db: AsyncSession, user: "models.User", product):
    if product.price_type != "coin":
        return None, "Bu mahsulot faqat pulga sotib olinadi"
    if product.seller_user_id == user.id:
        return None, "O'z mahsulotingizni sotib ololmaysiz"

    if product.catalog == "seller":
        voucher = await get_user_active_voucher(db, user)
        if voucher is None:
            return None, "Bu mahsulotni sotib olish uchun faol vaucher kerak"
        used = await _count_voucher_purchases(db, user, voucher, price_type="coin")
        product_for_voucher = await get_product(db, voucher.product_id)
        limit = product_for_voucher.voucher_product_count or 0
        if used >= limit:
            return None, "Vaucher limiti tugagan"

    if float(user.b_coin) < float(product.price_amount):
        return None, "B Coin yetarli emas"

    user.b_coin = float(user.b_coin) - float(product.price_amount)

    if product.catalog == "vaucher":
        from datetime import datetime, timedelta, timezone

        expires = datetime.now(timezone.utc) + timedelta(days=product.voucher_days or 3)
        db.add(models.UserVoucher(user_id=user.id, product_id=product.id, is_vip_plus=product.is_vip_plus, expires_at=expires))
    else:
        db.add(
            models.UserInventoryItem(
                user_id=user.id, product_id=product.id,
                purchase_price=product.price_amount, purchase_price_type="coin",
            )
        )
        if product.seller_user_id:
            seller = await get_user_by_id(db, product.seller_user_id)
            if seller:
                seller.b_coin = float(seller.b_coin) + float(product.price_amount)

    await db.commit()
    await db.refresh(user)
    await dispatch_mission_event(db, user, "product_purchased")
    await write_admin_log(
        db, user.telegram_id, "purchase_coin",
        f"product_id={product.id} name={product.name} price={product.price_amount}",
    )
    return True, "Xarid muvaffaqiyatli"


async def _count_voucher_purchases(db: AsyncSession, user: "models.User", voucher, price_type: str) -> int:
    result = await db.execute(
        select(func.count(models.UserInventoryItem.id))
        .join(models.Product, models.Product.id == models.UserInventoryItem.product_id)
        .where(
            models.UserInventoryItem.user_id == user.id,
            models.Product.catalog == "seller",
            models.UserInventoryItem.purchase_price_type == price_type,
            models.UserInventoryItem.acquired_at >= voucher.started_at,
        )
    )
    return result.scalar_one()


async def create_payment_order(db: AsyncSession, user: "models.User", product):
    from datetime import datetime, timedelta, timezone

    if product.price_type != "money":
        return None, "Bu mahsulot B Coinga sotib olinadi"
    if product.seller_user_id == user.id:
        return None, "O'z mahsulotingizni sotib ololmaysiz"

    if product.catalog == "seller":
        voucher = await get_user_active_voucher(db, user)
        if voucher is None or not voucher.is_vip_plus:
            return None, "Bu pullik mahsulotni sotib olish uchun VIP Plus vaucher kerak"
        used = await _count_voucher_purchases(db, user, voucher, price_type="money")
        product_for_voucher = await get_product(db, voucher.product_id)
        if used >= (product_for_voucher.voucher_paid_count or 0):
            return None, "VIP Plus limiti tugagan"

    approver_role = "seller" if (product.catalog == "seller" and product.seller_user_id) else "admin"
    now = datetime.now(timezone.utc)
    order = models.PaymentOrder(
        user_id=user.id,
        product_id=product.id,
        amount=product.price_amount,
        status="awaiting_screenshot",
        approver_role=approver_role,
        expires_at=now + timedelta(minutes=settings.PAYMENT_TIMEOUT_MINUTES),
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order, "OK"


async def get_latest_awaiting_order(db: AsyncSession, user: "models.User"):
    from datetime import datetime, timezone

    result = await db.execute(
        select(models.PaymentOrder)
        .where(models.PaymentOrder.user_id == user.id, models.PaymentOrder.status == "awaiting_screenshot")
        .order_by(models.PaymentOrder.created_at.desc())
    )
    order = result.scalars().first()
    if order is None:
        return None
    expires = order.expires_at if order.expires_at.tzinfo else order.expires_at.replace(tzinfo=timezone.utc)
    if expires < datetime.now(timezone.utc):
        order.status = "expired"
        await db.commit()
        return None
    return order


async def finalize_payment_order(db: AsyncSession, order, approved: bool):
    from datetime import datetime, timezone

    order.status = "approved" if approved else "rejected"
    order.decided_at = datetime.now(timezone.utc)
    if approved:
        user = await get_user_by_id(db, order.user_id)
        product = await get_product(db, order.product_id)
        if product.catalog == "premium":
            if user.premium_tier < (product.premium_tier or 0):
                user.premium_tier = product.premium_tier
        elif product.catalog == "vaucher":
            from datetime import timedelta

            expires = datetime.now(timezone.utc) + timedelta(days=product.voucher_days or 30)
            db.add(models.UserVoucher(user_id=user.id, product_id=product.id, is_vip_plus=product.is_vip_plus, expires_at=expires))
        else:
            db.add(
                models.UserInventoryItem(
                    user_id=user.id, product_id=product.id,
                    purchase_price=product.price_amount, purchase_price_type="money",
                )
            )
        await db.commit()
        await dispatch_mission_event(db, user, "product_purchased")
        await write_admin_log(
            db, user.telegram_id, "purchase_money_approved",
            f"order_id={order.id} product_id={product.id} name={product.name} amount={order.amount}",
        )
    else:
        await db.commit()
        buyer = await get_user_by_id(db, order.user_id)
        product = await get_product(db, order.product_id)
        await write_admin_log(
            db, buyer.telegram_id if buyer else None, "purchase_money_rejected",
            f"order_id={order.id} product_id={order.product_id} name={product.name if product else '—'} amount={order.amount}",
        )


async def get_user_inventory(db: AsyncSession, user: "models.User"):
    result = await db.execute(
        select(models.UserInventoryItem, models.Product)
        .join(models.Product, models.Product.id == models.UserInventoryItem.product_id)
        .where(models.UserInventoryItem.user_id == user.id, models.UserInventoryItem.status != "refunded")
        .order_by(models.UserInventoryItem.acquired_at.desc())
    )
    return result.all()


async def apply_inventory_item(db: AsyncSession, user: "models.User", item_id: int):
    item = await db.get(models.UserInventoryItem, item_id)
    if item is None or item.user_id != user.id:
        return False, "Mahsulot topilmadi"
    item.status = "applied"
    await db.commit()
    return True, "Qo'llanildi"


async def refund_inventory_item(db: AsyncSession, user: "models.User", item_id: int):
    item = await db.get(models.UserInventoryItem, item_id)
    if item is None or item.user_id != user.id:
        return False, "Mahsulot topilmadi"
    if item.status == "refunded":
        return False, "Allaqachon qaytarilgan"
    refund_amount = float(item.purchase_price) * 0.5
    user.b_coin = float(user.b_coin) + refund_amount
    item.status = "refunded"
    # Eslatma: "Sotuvchidan coin olinmaydi" — sotuvchi hisobidan hech narsa yechilmaydi.
    await db.commit()
    return True, f"{refund_amount:.2f} B Coin qaytarildi"


# ============================================================
# 3-bosqich: Oylik missiyalar
# ============================================================

def _current_period() -> str:
    from datetime import date

    today = date.today()
    return f"{today.year:04d}-{today.month:02d}"


async def get_active_monthly_missions(db: AsyncSession):
    result = await db.execute(
        select(models.MonthlyMission).where(models.MonthlyMission.is_active == True)  # noqa: E712
    )
    return list(result.scalars().all())


async def get_monthly_progress(db: AsyncSession, user: "models.User", mission):
    period = _current_period()
    result = await db.execute(
        select(models.UserMonthlyMissionProgress).where(
            models.UserMonthlyMissionProgress.user_id == user.id,
            models.UserMonthlyMissionProgress.mission_id == mission.id,
            models.UserMonthlyMissionProgress.period == period,
        )
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        progress = models.UserMonthlyMissionProgress(user_id=user.id, mission_id=mission.id, period=period)
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
    return progress


async def increment_monthly_mission_progress(db: AsyncSession, user: "models.User", mission_key: str, amount: int = 1):
    result = await db.execute(
        select(models.MonthlyMission).where(
            models.MonthlyMission.key == mission_key, models.MonthlyMission.is_active == True  # noqa: E712
        )
    )
    mission = result.scalar_one_or_none()
    if mission is None:
        return
    progress = await get_monthly_progress(db, user, mission)
    if progress.completed:
        return
    progress.progress += amount
    if progress.progress >= mission.requirement_count:
        progress.completed = True
    await db.commit()


# ============================================================
# 4-bosqich: Missiya voqealari (event-based tracking) + kunlik/oylik rotatsiya
# ============================================================

def _rotation_pick(pool: list, seed: str, n: int) -> list:
    """Berilgan ro'yxatdan seed (kun/oy) asosida barqaror n ta elementni tanlaydi —
    bir xil kun/oy davomida barcha foydalanuvchilarga bir xil to'plam ko'rinadi."""
    rng = random.Random(seed)
    pool_copy = list(pool)
    rng.shuffle(pool_copy)
    return pool_copy[:n]


async def get_today_daily_missions(db: AsyncSession) -> list:
    from datetime import date

    all_missions = await get_active_daily_missions(db)
    return _rotation_pick(all_missions, date.today().isoformat(), 3)


async def get_this_month_monthly_missions(db: AsyncSession) -> list:
    all_missions = await get_active_monthly_missions(db)
    return _rotation_pick(all_missions, _current_period(), 5)


async def dispatch_mission_event(db: AsyncSession, user: "models.User", event_type: str, amount: int = 1) -> None:
    """Real o'yin voqealarini bugungi/shu oygi ko'rsatilayotgan missiyalar
    progressiga bog'laydi. Faqat hozir "rotatsiyada" turgan missiyalar
    progress oladi (kunlik: 3 ta, oylik: 5 ta) — bu foydalanuvchi ekranida
    ko'rib turgan missiyalar bilan mos keladi."""
    daily_pool = await get_today_daily_missions(db)
    for m in daily_pool:
        if m.trigger_event == event_type:
            await increment_mission_progress(db, user, m.key, amount)

    monthly_pool = await get_this_month_monthly_missions(db)
    for m in monthly_pool:
        if m.trigger_event == event_type:
            await increment_monthly_mission_progress(db, user, m.key, amount)


# ============================================================
# 4-bosqich: Admin loglari
# ============================================================

async def write_admin_log(db: AsyncSession, actor_telegram_id: int | None, action: str, details: str = "") -> None:
    db.add(models.AdminLog(actor_telegram_id=actor_telegram_id, action=action, details=details))
    await db.commit()


async def get_recent_logs(db: AsyncSession, action_filter: str | None = None, limit: int = 100):
    stmt = select(models.AdminLog).order_by(models.AdminLog.created_at.desc())
    if action_filter:
        stmt = stmt.where(models.AdminLog.action == action_filter)
    result = await db.execute(stmt.limit(limit))
    return list(result.scalars().all())


async def get_voucher_status(db: AsyncSession, user: "models.User") -> dict:
    """Foydalanuvchining joriy faol vaucher holati — Profil/Do'kon sahifalarida
    ko'rsatish va "Mahsulot joylash" tugmasini ko'rsatish/yashirish uchun."""
    voucher = await get_user_active_voucher(db, user)
    if voucher is None:
        return {
            "has_active_voucher": False, "is_vip_plus": False, "expires_at": None,
            "product_quota_used": 0, "product_quota_total": 0,
            "paid_quota_used": 0, "paid_quota_total": 0,
        }
    product = await get_product(db, voucher.product_id)
    used_coin = await _count_voucher_purchases(db, user, voucher, price_type="coin")
    used_money = await _count_voucher_purchases(db, user, voucher, price_type="money") if voucher.is_vip_plus else 0
    return {
        "has_active_voucher": True,
        "is_vip_plus": voucher.is_vip_plus,
        "expires_at": voucher.expires_at.isoformat(),
        "product_quota_used": used_coin,
        "product_quota_total": (product.voucher_product_count or 0) if product else 0,
        "paid_quota_used": used_money,
        "paid_quota_total": (product.voucher_paid_count or 0) if (product and voucher.is_vip_plus) else 0,
                                         }
