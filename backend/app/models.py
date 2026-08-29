"""
Bilim Jangi — 1-bosqich ma'lumotlar bazasi modellari.

E'TIBOR: Bu 1-bosqich (asosiy skelet) modellari:
  - Foydalanuvchi, savollar banki, kunlik missiyalar, 1v1 Bot duel tarixi.
Keyingi bosqichlarda: Duel(odam bilan), OmmaviyDuel, Turnir, Do'stlik,
Do'kon/Mahsulot, Premium, Vaucher, To'lov, Sklad, AdminLog jadvallari
shu faylga (yoki alohida modul fayllariga) qo'shiladi — mavjud jadvallarga
tegmagan holda.
"""
from datetime import datetime, date

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True, nullable=False)
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(128), default="")
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    level: Mapped[int] = mapped_column(Integer, default=1)
    correct_answers_total: Mapped[int] = mapped_column(Integer, default=0)
    b_coin: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    # --- 2-bosqich: 1v1 (odam bilan) va ommaviy duel reytingi uchun ---
    wins_1v1: Mapped[int] = mapped_column(Integer, default=0)
    duels_played_1v1: Mapped[int] = mapped_column(Integer, default=0)
    mass_duel_score: Mapped[int] = mapped_column(Integer, default=0)
    turnir_wins: Mapped[int] = mapped_column(Integer, default=0)  # 3-bosqichda Turnir bilan to'ldiriladi

    # --- 3-bosqich: Premium, Do'kon ---
    premium_tier: Mapped[int] = mapped_column(Integer, default=0)  # 0=yo'q, 1..4

    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    mission_progress: Mapped[list["UserDailyMissionProgress"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    option_a: Mapped[str] = mapped_column(String(255), nullable=False)
    option_b: Mapped[str] = mapped_column(String(255), nullable=False)
    option_c: Mapped[str] = mapped_column(String(255), nullable=False)
    option_d: Mapped[str] = mapped_column(String(255), nullable=False)
    correct_option: Mapped[str] = mapped_column(String(1), nullable=False)  # "A"/"B"/"C"/"D"
    difficulty: Mapped[str] = mapped_column(String(16), default="medium")  # easy/medium/hard
    category: Mapped[str] = mapped_column(String(64), default="umumiy")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyMission(Base):
    """Admin panel orqali B Coin mukofoti belgilanadigan kunlik missiya shabloni."""

    __tablename__ = "daily_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="")
    requirement_count: Mapped[int] = mapped_column(Integer, default=1)
    reward_coin: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_event: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # correct_answer / invite_friend / duel_win / human_duel_played /
    # mass_duel_played / tournament_played / product_purchased / gift_sent


class UserDailyMissionProgress(Base):
    __tablename__ = "user_daily_mission_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    mission_id: Mapped[int] = mapped_column(ForeignKey("daily_missions.id", ondelete="CASCADE"))
    mission_date: Mapped[date] = mapped_column(Date, default=date.today)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["User"] = relationship(back_populates="mission_progress")
    mission: Mapped["DailyMission"] = relationship()


class FriendRequest(Base):
    """Do'stlik so'rovi. Qabul qilinsa (status='accepted') ikkala tomon ham
    bir-birining do'stlar ro'yxatida ko'rinadi (alohida Friendship jadvali
    shart emas — status='accepted' yozuvning o'zi do'stlikni bildiradi)."""

    __tablename__ = "friend_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    to_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/accepted/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class HumanDuel(Base):
    """👤 Odam bilan 1v1 Duel — navbat bilan savollarga javob beriladi."""

    __tablename__ = "human_duels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    invite_code: Mapped[str] = mapped_column(String(12), unique=True, index=True)

    player1_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    player2_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    status: Mapped[str] = mapped_column(String(24), default="waiting_for_opponent")
    # waiting_for_opponent / active / finished / cancelled

    question_ids: Mapped[str] = mapped_column(Text)  # vergul bilan ajratilgan savol ID'lari
    total_questions: Mapped[int] = mapped_column(Integer, default=10)
    current_index: Mapped[int] = mapped_column(Integer, default=0)

    player1_correct: Mapped[int] = mapped_column(Integer, default=0)
    player2_correct: Mapped[int] = mapped_column(Integer, default=0)

    winner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MassDuel(Base):
    """🌍 Ommaviy Duel — foydalanuvchi yoki admin tashkil qiladi, ko'p kishi qatnashadi."""

    __tablename__ = "mass_duels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_admin_duel: Mapped[bool] = mapped_column(Boolean, default=False)

    max_participants: Mapped[int] = mapped_column(Integer, default=50)
    option_count: Mapped[int] = mapped_column(Integer, default=4)  # 3 yoki 4 variantli savollar

    status: Mapped[str] = mapped_column(String(16), default="open")  # open/closed
    fund: Mapped[float] = mapped_column(Numeric(12, 2), default=0)  # xato javoblardan yig'ilgan jamg'arma

    last_question_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MassDuelParticipant(Base):
    __tablename__ = "mass_duel_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    duel_id: Mapped[int] = mapped_column(ForeignKey("mass_duels.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_helper: Mapped[bool] = mapped_column(Boolean, default=False)
    score: Mapped[int] = mapped_column(Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MassDuelQuestion(Base):
    __tablename__ = "mass_duel_questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    duel_id: Mapped[int] = mapped_column(ForeignKey("mass_duels.id", ondelete="CASCADE"))
    owner_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    option_a: Mapped[str] = mapped_column(String(255))
    option_b: Mapped[str] = mapped_column(String(255))
    option_c: Mapped[str] = mapped_column(String(255))
    option_d: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correct_option: Mapped[str] = mapped_column(String(1))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MassDuelAnswer(Base):
    __tablename__ = "mass_duel_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    duel_id: Mapped[int] = mapped_column(ForeignKey("mass_duels.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("mass_duel_questions.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    coin_change: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BotDuelLog(Base):
    """1v1 Bot bilan duel — har bir javob shu yerda qayd etiladi (statistika uchun)."""

    __tablename__ = "bot_duel_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    coin_change: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# 3-bosqich: Turnir
# ============================================================

class Tournament(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(12), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(128))

    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_admin_tournament: Mapped[bool] = mapped_column(Boolean, default=False)

    max_participants: Mapped[int] = mapped_column(Integer, default=100)
    prize_text: Mapped[str] = mapped_column(String(512), default="")

    question_ids: Mapped[str] = mapped_column(Text)  # vergul bilan ajratilgan
    total_questions: Mapped[int] = mapped_column(Integer, default=15)

    status: Mapped[str] = mapped_column(String(16), default="open")  # open/closed
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    score: Mapped[int] = mapped_column(Integer, default=0)
    current_index: Mapped[int] = mapped_column(Integer, default=0)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TournamentAnswer(Base):
    __tablename__ = "tournament_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    coin_change: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


# ============================================================
# 3-bosqich: Do'kon / Mahsulot / Sklad / Premium / Vaucher
# ============================================================

class Product(Base):
    """Do'kon mahsuloti — Premium tarif, Vaucher, ramka, nik bezagi, orqa fon,
    badge yoki sotuvchi tomonidan joylangan oddiy mahsulot bo'lishi mumkin."""

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    catalog: Mapped[str] = mapped_column(String(24))
    # premium / vaucher / frame / nick_decor / background / badge / seller

    name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(String(1024), default="")
    image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)

    price_type: Mapped[str] = mapped_column(String(8), default="coin")  # coin / money
    price_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    # Premium tarifga xos qo'shimcha maydonlar
    premium_tier: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1..4
    bonus_percent: Mapped[int | None] = mapped_column(Integer, nullable=True)  # +10/+30/+50/+80

    # Vaucherga xos qo'shimcha maydonlar
    voucher_days: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 3/7/30
    voucher_product_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    voucher_paid_count: Mapped[int | None] = mapped_column(Integer, nullable=True)  # VIP Plus uchun
    is_vip_plus: Mapped[bool] = mapped_column(Boolean, default=False)

    seller_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)  # sotuvchi mahsuloti admin tasdig'ini kutadi
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False)  # vaucher tugaganda yashiriladi (bazadan o'chmaydi)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserInventoryItem(Base):
    """📦 Sklad — foydalanuvchi sotib olgan mahsulot."""

    __tablename__ = "user_inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    purchase_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    purchase_price_type: Mapped[str] = mapped_column(String(8), default="coin")
    status: Mapped[str] = mapped_column(String(16), default="owned")  # owned/applied/refunded
    acquired_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserVoucher(Base):
    __tablename__ = "user_vouchers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    is_vip_plus: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PaymentOrder(Base):
    """💳 To'lov — pulga sotib olingan Premium/VIP Vaucher/Sotuvchi mahsuloti uchun
    screenshot tasdiqlash oqimi."""

    __tablename__ = "payment_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    status: Mapped[str] = mapped_column(String(24), default="awaiting_screenshot")
    # awaiting_screenshot / pending_approval / approved / rejected / expired / escalated_to_admin

    screenshot_file_id: Mapped[str | None] = mapped_column(String(256), nullable=True)
    approver_role: Mapped[str] = mapped_column(String(16), default="admin")  # admin / seller

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ============================================================
# 3-bosqich: Oylik missiyalar (kunlik bilan bir xil naqsh)
# ============================================================

class MonthlyMission(Base):
    __tablename__ = "monthly_missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(512), default="")
    requirement_count: Mapped[int] = mapped_column(Integer, default=1)
    reward_coin: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger_event: Mapped[str | None] = mapped_column(String(32), nullable=True)


class UserMonthlyMissionProgress(Base):
    __tablename__ = "user_monthly_mission_progress"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    mission_id: Mapped[int] = mapped_column(ForeignKey("monthly_missions.id", ondelete="CASCADE"))
    period: Mapped[str] = mapped_column(String(7))  # "2026-08" format
    progress: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    claimed: Mapped[bool] = mapped_column(Boolean, default=False)


# ============================================================
# 4-bosqich: Admin Panel — Loglar
# ============================================================

class AdminLog(Base):
    """📝 Admin amallari, xaridlar va coin o'zgarishlari tarixi."""

    __tablename__ = "admin_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    actor_telegram_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    action: Mapped[str] = mapped_column(String(64))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
