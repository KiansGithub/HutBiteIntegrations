from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    APP_BASE_URL: AnyHttpUrl = "http://localhost:8000"
    SESSION_SECRET: str = "dev_change_me"

    HUBRISE_OAUTH_URL: AnyHttpUrl = "https://manager.hubrise.com/oauth2/v1"
    HUBRISE_API_URL: AnyHttpUrl = "https://api.hubrise.com/v1"

    # Make these optional with defaults, not required
    HUBRISE_CLIENT_ID: Optional[str] = None
    HUBRISE_CLIENT_SECRET: Optional[str] = None
    HUBRISE_SCOPE: str = "profile,location[orders.write,catalog.read]"

    HUBRISE_ACCESS_TOKEN: Optional[str] = None
    HUBRISE_ACCOUNT_ID: Optional[str] = None
    HUBRISE_LOCATION_ID: Optional[str] = None
    HUBRISE_CATALOG_ID: Optional[str] = None

    POSTCODES_BASE_URL: str = "https://api.postcodes.io"
    POSTCODE_TTL_SECONDS: int = 86400
    HTTP_TIMEOUT_SECONDS: int = 6

    SMS_ENABLED: bool = False
    CLICKSEND_USERNAME: Optional[str] = None
    CLICKSEND_API_KEY: Optional[str] = None
    SMS_SENDER: Optional[str] = None

    class Config:
        # point to your chosen .env location; root is typical:
        env_file = Path(__file__).resolve().parents[2] / ".env"
        extra = "ignore"

settings = Settings()
