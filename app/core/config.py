from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional
import os

class Settings(BaseSettings):
    APP_BASE_URL: AnyHttpUrl = "http://localhost:8000"
    SESSION_SECRET: str = "dev_change_me"

    HUBRISE_OAUTH_URL: AnyHttpUrl = "https://manager.hubrise.com/oauth2/v1"
    HUBRISE_API_URL: AnyHttpUrl = "https://api.hubrise.com/v1"

    HUBRISE_CLIENT_ID: str
    HUBRISE_CLIENT_SECRET: str
    HUBRISE_SCOPE: str = "profile,location[orders.write,catalog.read]"

    # Optional: default fallbacks if not carried in session
    DEFAULT_LOCATION_ID: Optional[str] = None  # e.g. "159yd-0"

    class Config:
        env_file = ".env"

settings = Settings()
