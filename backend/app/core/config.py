from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        # Railway gives postgresql://, but we need postgresql+asyncpg://
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # Telegram
    TELEGRAM_BOT_TOKEN: str
    ADMIN_CHAT_ID: int  # Telegram group/chat ID for admin notifications

    # App
    DEBUG: bool = False

    # Game Economics
    EVOLUTION_FEE_PERCENT: float = 0.10  # 10% fee on upgrades (doesn't add to invested_total)

    class Config:
        env_file = ".env"


settings = Settings()
