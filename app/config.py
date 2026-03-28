from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/offerpilot"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    SECRET_KEY: str = "dev-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # WeChat
    WECHAT_APP_ID: str = ""
    WECHAT_APP_SECRET: str = ""

    # SMS (Aliyun)
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_SMS_SIGN_NAME: str = "OfferPilot"
    ALIYUN_SMS_TEMPLATE_CODE: str = ""

    # AI
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"

    # Apple IAP
    APPLE_BUNDLE_ID: str = "com.offerpilot.app"
    APPLE_SHARED_SECRET: str = ""

    # App
    DEBUG: bool = True
    CORS_ORIGINS: str = '["http://localhost:3000"]'

    def get_cors_origins(self) -> List[str]:
        return json.loads(self.CORS_ORIGINS)


settings = Settings()
