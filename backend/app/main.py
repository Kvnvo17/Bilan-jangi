"""
Bilim Jangi — FastAPI asosiy ilova.
Backend API + Telegram Web App (static frontend) + Admin Panel + aiogram bot
bitta process ichida ishlaydi (Render Free Web Service uchun mos).
"""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import FileResponse

from app.admin import router as admin_router
from app.api.duel import router as duel_router
from app.api.duel_human import router as duel_human_router
from app.api.friends import router as friends_router
from app.api.mass_duel import router as mass_duel_router
from app.api.missions import router as missions_router
from app.api.monthly_missions import router as monthly_missions_router
from app.api.payment import router as payment_router
from app.api.profile import router as profile_router
from app.api.ranking import router as ranking_router
from app.api.shop import router as shop_router
from app.api.tournament import router as tournament_router
from app.bot.bot import run_bot_background_task
from app.config import settings
from app.database import AsyncSessionLocal, init_models
from app.seed import run_all_seeds

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("bilim_jangi.main")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"
ADMIN_STATIC_DIR = PROJECT_ROOT / "admin_panel" / "static"

_bot_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Bilim Jangi ilovasi ishga tushmoqda...")
    await init_models()
    async with AsyncSessionLocal() as db:
        await run_all_seeds(db)

    global _bot_task
    if settings.BOT_TOKEN and settings.BOT_TOKEN != "PUT_YOUR_BOT_TOKEN_HERE":
        _bot_task = run_bot_background_task()
        logger.info("Telegram bot background task ishga tushdi")
    else:
        logger.warning("BOT_TOKEN sozlanmagan — bot ishga tushmadi (faqat API/WebApp ishlaydi)")

    yield

    if _bot_task:
        _bot_task.cancel()
    logger.info("Bilim Jangi ilovasi to'xtatildi")


app = FastAPI(title="Bilim Jangi API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# --- API routerlar ---
app.include_router(profile_router)
app.include_router(duel_router)
app.include_router(missions_router)
app.include_router(admin_router)
# 2-bosqich
app.include_router(duel_human_router)
app.include_router(mass_duel_router)
app.include_router(friends_router)
app.include_router(ranking_router)
# 3-bosqich
app.include_router(tournament_router)
app.include_router(shop_router)
app.include_router(payment_router)
app.include_router(monthly_missions_router)


# --- Health check (UptimeRobot uchun) ---
@app.get("/health")
async def health():
    return {"status": "ok", "service": "bilim-jangi"}


# --- Admin panel statik fayllari (CSS) ---
app.mount("/admin-static", StaticFiles(directory=str(ADMIN_STATIC_DIR)), name="admin-static")

# --- Telegram Web App frontend (statik) ---
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend-static")


@app.get("/")
async def serve_webapp_index():
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/tutorial")
async def serve_tutorial():
    tutorial_path = FRONTEND_DIR / "tutorial.html"
    if tutorial_path.exists():
        return FileResponse(str(tutorial_path))
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/duel")
async def serve_duel_page():
    return FileResponse(str(FRONTEND_DIR / "duel.html"))


@app.get("/human-duel")
async def serve_human_duel_page():
    return FileResponse(str(FRONTEND_DIR / "human_duel.html"))


@app.get("/mass-duel")
async def serve_mass_duel_list_page():
    return FileResponse(str(FRONTEND_DIR / "mass_duel_list.html"))


@app.get("/mass-duel/room")
async def serve_mass_duel_room_page():
    return FileResponse(str(FRONTEND_DIR / "mass_duel_room.html"))


@app.get("/friends")
async def serve_friends_page():
    return FileResponse(str(FRONTEND_DIR / "friends.html"))


@app.get("/ranking")
async def serve_ranking_page():
    return FileResponse(str(FRONTEND_DIR / "ranking.html"))


@app.get("/tournament")
async def serve_tournament_list_page():
    return FileResponse(str(FRONTEND_DIR / "tournament_list.html"))


@app.get("/tournament/room")
async def serve_tournament_room_page():
    return FileResponse(str(FRONTEND_DIR / "tournament_room.html"))


@app.get("/shop")
async def serve_shop_page():
    return FileResponse(str(FRONTEND_DIR / "shop.html"))


@app.get("/shop/product")
async def serve_shop_product_page():
    return FileResponse(str(FRONTEND_DIR / "shop_product.html"))


@app.get("/shop/sell")
async def serve_shop_sell_page():
    return FileResponse(str(FRONTEND_DIR / "shop_sell.html"))


@app.get("/sklad")
async def serve_sklad_page():
    return FileResponse(str(FRONTEND_DIR / "sklad.html"))


@app.get("/monthly-missions")
async def serve_monthly_missions_page():
    return FileResponse(str(FRONTEND_DIR / "monthly_missions.html"))
