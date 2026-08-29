"""
Bilim Jangi — Telegram bot (aiogram 3.x).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
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
    "Assalomu alaykum! Bilim Jangi'ga xush kelibsiz.\n\n"
    "🧠 Bilimingizni sinang\n"
    "💰 B Coin yig'ing\n"
    "🏆 Turnirlarda qatnashing"
)


def build_start_keyboard() -> InlineKeyboardMarkup:
    webapp_url = settings.WEBAPP_URL.rstrip("/")

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🧠 Bilim Jangi",
                    web_app=WebAppInfo(url=webapp_url)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📢 Yangiliklar",
                    url=settings.ADMIN_CHANNEL_URL
                ),
                InlineKeyboardButton(
                    text="🆘 Yordam",
                    url=f"https://t.me/{settings.ADMIN_USERNAME}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 O‘rganish",
                    web_app=WebAppInfo(
                        url=f"{webapp_url}/tutorial"
                    )
                )
            ]
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"/start -> {message.from_user.id}")

    keyboard = build_start_keyboard()

    try:
        if settings.START_PHOTO_URL:
            await message.answer_photo(
                photo=settings.START_PHOTO_URL,
                caption=WELCOME_TEXT,
                reply_markup=keyboard
            )
        else:
            await message.answer(
                WELCOME_TEXT,
                reply_markup=keyboard
            )

    except Exception as e:
        logger.exception(f"START ERROR: {e}")

        await message.answer(
            WELCOME_TEXT,
            reply_markup=keyboard
        )


def create_bot_and_dispatcher():
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML
        )
    )

    dp = Dispatcher()

    dp.include_router(router)
    dp.include_router(payment_router)

    return bot, dp


async def start_polling():
    logger.info("========== BOT START ==========")

    bot, dp = create_bot_and_dispatcher()

    try:
        me = await bot.get_me()
        logger.info(f"Bot: @{me.username}")

        await bot.delete_webhook(
            drop_pending_updates=True
        )

        logger.info("Polling boshlandi")

        await dp.start_polling(bot)

    except Exception as e:
        logger.exception(f"BOT ERROR: {e}")


def run_bot_background_task():
    logger.info("Background task yaratildi")
    return asyncio.create_task(start_polling())