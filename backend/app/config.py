"""
Bilim Jangi — konfiguratsiya.
Barcha maxfiy va muhim sozlamalar .env fayldan o'qiladi.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Telegram
    BOT_TOKEN: str
    ADMIN_TELEGRAM_ID: int = 0
    ADMIN_CHANNEL_URL: str = "https://t.me/"
    ADMIN_USERNAME: str = "admin"
    START_PHOTO_URL: str = ""

    # --- 3-bosqich: To'lov (screenshot tasdiqlash) ---
    PAYMENT_CARD_NUMBER: str = "0000 0000 0000 0000"
    PAYMENT_CARD_HOLDER: str = "Bilim Jangi"
    PAYMENT_TIMEOUT_MINUTES: int = 30

    # Web App
    WEBAPP_URL: str = "https://example.onrender.com"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/bilimjangi"

    # Admin panel (Jinja2 login)
    ADMIN_PANEL_USERNAME: str = "admin"
    ADMIN_PANEL_PASSWORD: str = "change_me"
    SECRET_KEY: str = "change_this_secret_key"

    # App
    ENV: str = "production"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
