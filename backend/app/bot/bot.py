"""
Bilim Jangi — Telegram bot (aiogram 3.x).
Polling rejimida ishga tushadi (FastAPI startup eventida background task sifatida).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.config import settings
from app.bot.payment_handlers import payment_router

logger = logging.getLogger("bilim_jangi.bot")

router = Router()

WELCOME_TEXT = (
    "Assalomu alaykum! Bilim Jangi'ga xush kelibsiz. "
    "Bilimingizni sinang, B Coin yig‘ing va turnirlarda g‘olib bo‘ling!"
)


def build_start_keyboard() -> InlineKeyboardMarkup:
    webapp_url = settings.WEBAPP_URL.rstrip("/")
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Bilim Jangi",
                    web_app=WebAppInfo(url=webapp_url),
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Yangiliklar", url=settings.ADMIN_CHANNEL_URL
                ),
                InlineKeyboardButton(
                    text="🆘 Yordam", url=f"https://t.me/{settings.ADMIN_USERNAME}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📚 O‘rganish",
                    web_app=WebAppInfo(url=f"{webapp_url}/tutorial"),
                )
            ],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    keyboard = build_start_keyboard()
    if settings.START_PHOTO_URL:
        try:
            await message.answer_photo(
                photo=settings.START_PHOTO_URL,
                caption=WELCOME_TEXT,
                reply_markup=keyboard,
            )
            return
        except Exception:
            logger.exception("START_PHOTO_URL yuborib bo'lmadi, matn bilan yuboriladi")
    await message.answer(WELCOME_TEXT, reply_markup=keyboard)


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(payment_router)
    return bot, dp


async def start_polling() -> None:
    bot, dp = create_bot_and_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bilim Jangi bot polling boshlandi")
    await dp.start_polling(bot)


def run_bot_background_task() -> asyncio.Task:
    """FastAPI startup eventidan chaqiriladi — botni background task sifatida ishga tushiradi."""
    return asyncio.create_task(start_polling())
