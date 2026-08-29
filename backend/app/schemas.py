from pydantic import BaseModel, Field


class ProfileSyncRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str = ""
    avatar_url: str | None = None


class ProfileOut(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str
    avatar_url: str | None
    level: int
    correct_answers_total: int
    b_coin: float
    is_admin: bool

    model_config = {"from_attributes": True}


class QuestionOut(BaseModel):
    id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    model_config = {"from_attributes": True}


class BotDuelAnswerRequest(BaseModel):
    telegram_id: int
    question_id: int
    selected_option: str = Field(pattern="^[ABCD]$")


class BotDuelAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    coin_change: float
    new_b_coin: float
    new_level: int
    leveled_up: bool


class DailyMissionOut(BaseModel):
    key: str
    title: str
    description: str
    requirement_count: int
    reward_coin: float
    progress: int
    completed: bool
    claimed: bool


class ClaimMissionRequest(BaseModel):
    telegram_id: int
    key: str


# ============================================================
# 2-bosqich: Do'stlar, Odam bilan Duel, Ommaviy Duel, Reyting
# ============================================================

class UserBrief(BaseModel):
    telegram_id: int
    username: str | None
    first_name: str
    avatar_url: str | None
    level: int
    b_coin: float

    model_config = {"from_attributes": True}


class FriendRequestOut(BaseModel):
    request_id: int
    user: UserBrief
    created_at: str


class SendFriendRequest(BaseModel):
    telegram_id: int
    target: str  # username (@ bilan yoki yo'q) yoki telegram_id raqami


class RespondFriendRequest(BaseModel):
    telegram_id: int
    request_id: int
    action: str = Field(pattern="^(accept|reject)$")


class GiftCoinRequest(BaseModel):
    telegram_id: int
    friend_telegram_id: int
    amount: float = Field(gt=0)


class SearchUsersResult(BaseModel):
    users: list[UserBrief]


# --- Odam bilan 1v1 Duel ---

class HumanDuelCreateRequest(BaseModel):
    telegram_id: int
    target: str | None = None  # username/telegram_id (bo'sh bo'lsa — faqat link orqali kutiladi)


class HumanDuelJoinRequest(BaseModel):
    telegram_id: int
    invite_code: str


class HumanDuelStateOut(BaseModel):
    invite_code: str
    status: str
    player1: UserBrief
    player2: UserBrief | None
    current_turn_telegram_id: int | None
    total_questions: int
    current_index: int
    player1_correct: int
    player2_correct: int
    winner_telegram_id: int | None
    current_question: QuestionOut | None = None


class HumanDuelAnswerRequest(BaseModel):
    telegram_id: int
    invite_code: str
    question_id: int
    selected_option: str = Field(pattern="^[ABCD]$")


class HumanDuelAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    coin_change: float
    duel_finished: bool
    winner_telegram_id: int | None


# --- Ommaviy Duel ---

class MassDuelCreateRequest(BaseModel):
    telegram_id: int
    name: str
    is_admin_duel: bool = False
    option_count: int = 4


class MassDuelJoinRequest(BaseModel):
    telegram_id: int
    code: str


class MassDuelOut(BaseModel):
    code: str
    name: str
    owner: UserBrief | None
    is_admin_duel: bool
    max_participants: int
    participant_count: int
    status: str
    fund: float


class MassDuelListOut(BaseModel):
    duels: list[MassDuelOut]


class MassDuelQuestionCreateRequest(BaseModel):
    telegram_id: int
    code: str
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str | None = None
    correct_option: str = Field(pattern="^[ABCD]$")


class MassDuelQuestionOut(BaseModel):
    id: int
    text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str | None

    model_config = {"from_attributes": True}


class MassDuelAnswerRequest(BaseModel):
    telegram_id: int
    code: str
    question_id: int
    selected_option: str = Field(pattern="^[ABCD]$")


class MassDuelAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    coin_change: float
    new_b_coin: float


class MassDuelCloseRequest(BaseModel):
    telegram_id: int
    code: str


class MassDuelLeaderboardEntry(BaseModel):
    user: UserBrief
    score: int


class MassDuelDetailOut(BaseModel):
    duel: MassDuelOut
    leaderboard: list[MassDuelLeaderboardEntry]


# --- Reyting ---

class RankingEntry(BaseModel):
    rank: int
    user: UserBrief
    score: int


# ============================================================
# 3-bosqich: Turnir
# ============================================================

class TournamentCreateRequest(BaseModel):
    telegram_id: int
    name: str
    is_admin_tournament: bool = False
    prize_text: str = ""
    total_questions: int = 15


class TournamentJoinRequest(BaseModel):
    telegram_id: int
    code: str


class TournamentOut(BaseModel):
    code: str
    name: str
    owner: UserBrief | None
    is_admin_tournament: bool
    max_participants: int
    participant_count: int
    prize_text: str
    total_questions: int
    status: str


class TournamentListOut(BaseModel):
    tournaments: list[TournamentOut]


class TournamentLeaderboardEntry(BaseModel):
    rank: int
    user: UserBrief
    score: int


class TournamentDetailOut(BaseModel):
    tournament: TournamentOut
    leaderboard: list[TournamentLeaderboardEntry]
    my_current_index: int
    my_score: int


class TournamentAnswerRequest(BaseModel):
    telegram_id: int
    code: str
    question_id: int
    selected_option: str = Field(pattern="^[ABCD]$")


class TournamentAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    coin_change: float
    finished_all_questions: bool


# ============================================================
# 3-bosqich: Do'kon / Sklad / Premium / Vaucher
# ============================================================

class ProductOut(BaseModel):
    id: int
    catalog: str
    name: str
    description: str
    image_url: str | None
    price_type: str
    price_amount: float
    premium_tier: int | None
    bonus_percent: int | None
    voucher_days: int | None
    voucher_product_count: int | None
    voucher_paid_count: int | None
    is_vip_plus: bool
    seller_user_id: int | None

    model_config = {"from_attributes": True}


class ProductListOut(BaseModel):
    products: list[ProductOut]


class ProductSubmitRequest(BaseModel):
    telegram_id: int
    catalog: str
    name: str
    description: str = ""
    image_url: str | None = None
    price_amount: float = Field(gt=0)


class PurchaseRequest(BaseModel):
    telegram_id: int
    product_id: int


class PurchaseCoinResult(BaseModel):
    detail: str
    new_b_coin: float


class PurchaseMoneyResult(BaseModel):
    order_id: int
    card_number: str
    card_holder: str
    amount: float
    expires_at: str
    instructions: str


class InventoryItemOut(BaseModel):
    id: int
    product: ProductOut
    status: str
    acquired_at: str


class InventoryListOut(BaseModel):
    items: list[InventoryItemOut]


class ApplyOrRefundRequest(BaseModel):
    telegram_id: int
    inventory_item_id: int


# ============================================================
# 3-bosqich: To'lov (screenshot)
# ============================================================

class PaymentStatusOut(BaseModel):
    order_id: int
    status: str
    product_name: str
    amount: float
    expires_at: str


# ============================================================
# 3-bosqich: Oylik missiyalar
# ============================================================

class MonthlyMissionOut(BaseModel):
    key: str
    title: str
    description: str
    requirement_count: int
    reward_coin: float
    progress: int
    completed: bool
    claimed: bool


class ClaimMonthlyMissionRequest(BaseModel):
    telegram_id: int
    key: str
