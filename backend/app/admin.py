"""
Bilim Jangi — 1-bosqich Admin Panel.
Kirish: /admin/login (ADMIN_PANEL_USERNAME / ADMIN_PANEL_PASSWORD, .env dan).
Session cookie orqali himoyalangan (starlette SessionMiddleware).

1-bosqichda: Dashboard (statistika) + Foydalanuvchilar (qidirish, B Coin
qo'shish/ayirish, ban/unban). Savollar/Missiyalar/Do'kon/Premium/Vaucher/
To'lovlar/Reklama/Loglar bo'limlari keyingi bosqichlarda shu faylga
qo'shiladi.
"""
from pathlib import Path
import random

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app import crud
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["admin"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "admin_panel" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("admin_logged_in"))


def require_admin(request: Request):
    if not is_logged_in(request):
        return False
    return True


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == settings.ADMIN_PANEL_USERNAME and password == settings.ADMIN_PANEL_PASSWORD:
        request.session["admin_logged_in"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(
        "login.html", {"request": request, "error": "Login yoki parol noto'g'ri"}
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)


@router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    total_users = (await db.execute(select(func.count(models.User.id)))).scalar_one()
    total_b_coin = (await db.execute(select(func.coalesce(func.sum(models.User.b_coin), 0)))).scalar_one()
    total_correct = (
        await db.execute(select(func.coalesce(func.sum(models.User.correct_answers_total), 0)))
    ).scalar_one()
    total_questions = (await db.execute(select(func.count(models.Question.id)))).scalar_one()
    banned_users = (
        await db.execute(select(func.count(models.User.id)).where(models.User.is_banned == True))  # noqa: E712
    ).scalar_one()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_users": total_users,
            "total_b_coin": float(total_b_coin),
            "total_correct": total_correct,
            "total_questions": total_questions,
            "banned_users": banned_users,
        },
    )


@router.get("/users", response_class=HTMLResponse)
async def users_list(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    from sqlalchemy import or_

    stmt = select(models.User).order_by(models.User.id.desc())
    if q:
        like = f"%{q}%"
        conditions = [models.User.username.ilike(like), models.User.first_name.ilike(like)]
        if q.isdigit():
            conditions.append(models.User.telegram_id == int(q))
        stmt = stmt.where(or_(*conditions))
    result = await db.execute(stmt.limit(100))
    users = result.scalars().all()

    return templates.TemplateResponse(
        "users.html", {"request": request, "users": users, "q": q}
    )


@router.post("/users/{user_id}/coin")
async def adjust_coin(
    request: Request, user_id: int, amount: float = Form(...), db: AsyncSession = Depends(get_db)
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    user = await db.get(models.User, user_id)
    if user:
        user.b_coin = float(user.b_coin) + amount
        await db.commit()
        await crud.write_admin_log(db, None, "coin_adjust", f"user_id={user_id} amount={amount}")
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/ban")
async def ban_user(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    user = await db.get(models.User, user_id)
    if user:
        user.is_banned = True
        await db.commit()
        await crud.write_admin_log(db, None, "ban_user", f"user_id={user_id}")
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/unban")
async def unban_user(request: Request, user_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    user = await db.get(models.User, user_id)
    if user:
        user.is_banned = False
        await db.commit()
        await crud.write_admin_log(db, None, "unban_user", f"user_id={user_id}")
    return RedirectResponse(url="/admin/users", status_code=302)


# ============================================================
# 3-bosqich: Mahsulotlarni tasdiqlash (sotuvchi joylagan mahsulotlar)
# ============================================================

@router.get("/products", response_class=HTMLResponse)
async def pending_products(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    result = await db.execute(
        select(models.Product, models.User)
        .join(models.User, models.User.id == models.Product.seller_user_id)
        .where(models.Product.is_approved == False)  # noqa: E712
        .order_by(models.Product.created_at.desc())
    )
    rows = result.all()
    return templates.TemplateResponse("products.html", {"request": request, "rows": rows})


@router.post("/products/{product_id}/approve")
async def approve_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    product = await db.get(models.Product, product_id)
    if product:
        product.is_approved = True
        await db.commit()
        await crud.write_admin_log(db, None, "product_approve", f"product_id={product_id} name={product.name}")
    return RedirectResponse(url="/admin/products", status_code=302)


@router.post("/products/{product_id}/reject")
async def reject_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    product = await db.get(models.Product, product_id)
    if product:
        product.is_active = False
        await db.commit()
        await crud.write_admin_log(db, None, "product_reject", f"product_id={product_id} name={product.name}")
    return RedirectResponse(url="/admin/products", status_code=302)


# ============================================================
# 4-bosqich: ❓ Savollar banki boshqaruvi
# ============================================================

@router.get("/questions", response_class=HTMLResponse)
async def questions_list(request: Request, q: str = "", db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    stmt = select(models.Question).order_by(models.Question.id.desc())
    if q:
        stmt = stmt.where(models.Question.text.ilike(f"%{q}%"))
    result = await db.execute(stmt.limit(100))
    questions = result.scalars().all()
    return templates.TemplateResponse("questions.html", {"request": request, "questions": questions, "q": q, "external": None})


@router.post("/questions/add")
async def add_question(
    request: Request,
    text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    difficulty: str = Form("medium"),
    category: str = Form("umumiy"),
    db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    db.add(
        models.Question(
            text=text, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d,
            correct_option=correct_option.upper()[:1], difficulty=difficulty, category=category,
        )
    )
    await db.commit()
    await crud.write_admin_log(db, None, "question_add", f"text={text[:60]}")
    return RedirectResponse(url="/admin/questions", status_code=302)


@router.post("/questions/{question_id}/edit")
async def edit_question(
    request: Request,
    question_id: int,
    text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    difficulty: str = Form("medium"),
    db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    question = await db.get(models.Question, question_id)
    if question:
        question.text = text
        question.option_a, question.option_b = option_a, option_b
        question.option_c, question.option_d = option_c, option_d
        question.correct_option = correct_option.upper()[:1]
        question.difficulty = difficulty
        await db.commit()
        await crud.write_admin_log(db, None, "question_edit", f"question_id={question_id}")
    return RedirectResponse(url="/admin/questions", status_code=302)


@router.post("/questions/{question_id}/delete")
async def delete_question(request: Request, question_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    question = await db.get(models.Question, question_id)
    if question:
        question.is_active = not question.is_active
        await db.commit()
        await crud.write_admin_log(db, None, "question_toggle_active", f"question_id={question_id} now_active={question.is_active}")
    return RedirectResponse(url="/admin/questions", status_code=302)


@router.get("/questions/fetch-external", response_class=HTMLResponse)
async def fetch_external_questions(request: Request, db: AsyncSession = Depends(get_db)):
    """Internetdan (Open Trivia DB — ochiq, bepul, ro'yxatdan o'tishsiz API)
    tasodifiy savollar oladi. Admin ko'rib chiqib, kerakli tarjima/tahrirdan
    so'ng "Bankka qo'shish" tugmasi bilan tasdiqlaydi."""
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    import html as html_lib
    import httpx

    external_questions = []
    error = None
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get("https://opentdb.com/api.php", params={"amount": 10, "type": "multiple"})
            data = resp.json()
        for item in data.get("results", []):
            options = item["incorrect_answers"] + [item["correct_answer"]]
            random.shuffle(options)
            correct_index = options.index(item["correct_answer"])
            external_questions.append(
                {
                    "text": html_lib.unescape(item["question"]),
                    "options": [html_lib.unescape(o) for o in options],
                    "correct_letter": "ABCD"[correct_index],
                    "category": html_lib.unescape(item.get("category", "umumiy")),
                    "difficulty": item.get("difficulty", "medium"),
                }
            )
    except Exception as exc:  # tarmoq muammosi, rate-limit va h.k.
        error = f"Tashqi API xatosi: {exc}"

    result = await db.execute(select(models.Question).order_by(models.Question.id.desc()).limit(100))
    questions = result.scalars().all()
    return templates.TemplateResponse(
        "questions.html",
        {"request": request, "questions": questions, "q": "", "external": external_questions, "external_error": error},
    )


@router.post("/questions/add-external")
async def add_external_question(
    request: Request,
    text: str = Form(...),
    option_a: str = Form(...),
    option_b: str = Form(...),
    option_c: str = Form(...),
    option_d: str = Form(...),
    correct_option: str = Form(...),
    category: str = Form("umumiy"),
    difficulty: str = Form("medium"),
    db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    db.add(
        models.Question(
            text=text, option_a=option_a, option_b=option_b, option_c=option_c, option_d=option_d,
            correct_option=correct_option.upper()[:1], difficulty=difficulty, category=category,
        )
    )
    await db.commit()
    await crud.write_admin_log(db, None, "question_add_external", f"text={text[:60]}")
    return RedirectResponse(url="/admin/questions/fetch-external", status_code=302)


# ============================================================
# 4-bosqich: 🎯 Missiyalar boshqaruvi (faqat B Coin mukofoti va holatini belgilash)
# ============================================================

@router.get("/missions", response_class=HTMLResponse)
async def missions_admin(request: Request, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    daily_result = await db.execute(select(models.DailyMission).order_by(models.DailyMission.id))
    monthly_result = await db.execute(select(models.MonthlyMission).order_by(models.MonthlyMission.id))
    return templates.TemplateResponse(
        "missions.html",
        {
            "request": request,
            "daily_missions": daily_result.scalars().all(),
            "monthly_missions": monthly_result.scalars().all(),
        },
    )


@router.post("/missions/daily/{mission_id}/update")
async def update_daily_mission(
    request: Request, mission_id: int, reward_coin: float = Form(...),
    is_active: str = Form("off"), db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    mission = await db.get(models.DailyMission, mission_id)
    if mission:
        mission.reward_coin = reward_coin
        mission.is_active = is_active == "on"
        await db.commit()
        await crud.write_admin_log(db, None, "daily_mission_update", f"mission_id={mission_id} reward={reward_coin}")
    return RedirectResponse(url="/admin/missions", status_code=302)


@router.post("/missions/monthly/{mission_id}/update")
async def update_monthly_mission(
    request: Request, mission_id: int, reward_coin: float = Form(...),
    is_active: str = Form("off"), db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    mission = await db.get(models.MonthlyMission, mission_id)
    if mission:
        mission.reward_coin = reward_coin
        mission.is_active = is_active == "on"
        await db.commit()
        await crud.write_admin_log(db, None, "monthly_mission_update", f"mission_id={mission_id} reward={reward_coin}")
    return RedirectResponse(url="/admin/missions", status_code=302)


# ============================================================
# 4-bosqich: 🛒 Do'kon boshqaruvi (Premium/Vaucher narxlari, kataloglar)
# ============================================================

@router.get("/shop", response_class=HTMLResponse)
async def shop_admin(request: Request, catalog: str = "", db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    stmt = select(models.Product).where(models.Product.is_active == True).order_by(models.Product.catalog, models.Product.id)  # noqa: E712
    if catalog:
        stmt = stmt.where(models.Product.catalog == catalog)
    result = await db.execute(stmt)
    products = result.scalars().all()
    return templates.TemplateResponse("shop.html", {"request": request, "products": products, "catalog": catalog})


@router.post("/shop/{product_id}/update")
async def update_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    description: str = Form(""),
    price_amount: float = Form(...),
    is_hidden: str = Form("off"),
    bonus_percent: int = Form(0),
    voucher_days: int = Form(0),
    voucher_product_count: int = Form(0),
    voucher_paid_count: int = Form(0),
    db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    product = await db.get(models.Product, product_id)
    if product:
        product.name = name
        product.description = description
        product.price_amount = price_amount
        product.is_hidden = is_hidden == "on"
        if product.catalog == "premium":
            product.bonus_percent = bonus_percent
        if product.catalog == "vaucher":
            product.voucher_days = voucher_days
            product.voucher_product_count = voucher_product_count
            if product.is_vip_plus:
                product.voucher_paid_count = voucher_paid_count
        await db.commit()
        await crud.write_admin_log(db, None, "product_update", f"product_id={product_id} price={price_amount}")
    return RedirectResponse(url="/admin/shop", status_code=302)


@router.post("/shop/{product_id}/delete")
async def delete_product(request: Request, product_id: int, db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    product = await db.get(models.Product, product_id)
    if product:
        product.is_active = False
        await db.commit()
        await crud.write_admin_log(db, None, "product_delete", f"product_id={product_id}")
    return RedirectResponse(url="/admin/shop", status_code=302)


# ============================================================
# 4-bosqich: 💳 To'lovlar tarixi
# ============================================================

@router.get("/payments", response_class=HTMLResponse)
async def payments_admin(request: Request, status: str = "", db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    stmt = (
        select(models.PaymentOrder, models.User, models.Product)
        .join(models.User, models.User.id == models.PaymentOrder.user_id)
        .join(models.Product, models.Product.id == models.PaymentOrder.product_id)
        .order_by(models.PaymentOrder.created_at.desc())
    )
    if status:
        stmt = stmt.where(models.PaymentOrder.status == status)
    result = await db.execute(stmt.limit(100))
    rows = result.all()
    return templates.TemplateResponse("payments.html", {"request": request, "rows": rows, "status": status})


# ============================================================
# 4-bosqich: 📢 Reklama (Broadcast)
# ============================================================

@router.get("/broadcast", response_class=HTMLResponse)
async def broadcast_page(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse("broadcast.html", {"request": request, "result": None})


@router.post("/broadcast/send", response_class=HTMLResponse)
async def broadcast_send(
    request: Request,
    text: str = Form(...),
    image_url: str = Form(""),
    button_text: str = Form(""),
    button_url: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)

    from aiogram import Bot
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    keyboard = None
    if button_text and button_url:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=button_text, url=button_url)]])

    result = await db.execute(select(models.User.telegram_id).where(models.User.is_banned == False))  # noqa: E712
    telegram_ids = [row[0] for row in result.all()]

    sent, failed = 0, 0
    bot = Bot(token=settings.BOT_TOKEN)
    try:
        for tg_id in telegram_ids:
            try:
                if image_url:
                    await bot.send_photo(tg_id, photo=image_url, caption=text, reply_markup=keyboard)
                else:
                    await bot.send_message(tg_id, text, reply_markup=keyboard)
                sent += 1
            except Exception:
                failed += 1
    finally:
        await bot.session.close()

    await crud.write_admin_log(db, None, "broadcast_sent", f"sent={sent} failed={failed} text={text[:60]}")

    return templates.TemplateResponse(
        "broadcast.html", {"request": request, "result": {"sent": sent, "failed": failed, "total": len(telegram_ids)}}
    )


# ============================================================
# 4-bosqich: 📝 Loglar
# ============================================================

@router.get("/logs", response_class=HTMLResponse)
async def logs_admin(request: Request, action: str = "", db: AsyncSession = Depends(get_db)):
    if not is_logged_in(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    logs = await crud.get_recent_logs(db, action_filter=action or None, limit=150)
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs, "action": action})
