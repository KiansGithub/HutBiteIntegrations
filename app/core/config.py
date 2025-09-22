from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    APP_BASE_URL: AnyHttpUrl = "http://localhost:8000"
    SESSION_SECRET: str = "dev_change_me"

    HUBRISE_OAUTH_URL: AnyHttpUrl = "https://manager.hubrise.com/oauth2/v1"
    HUBRISE_API_URL: AnyHttpUrl = "https://api.hubrise.com/v1"

    HUBRISE_CLIENT_ID: str
    HUBRISE_CLIENT_SECRET: str
    HUBRISE_SCOPE: str = "profile,location[orders.write,catalog.read]"

    # Optional: default fallbacks if not carried in session
    HUBRISE_ACCESS_TOKEN: Optional[str] = None 
    HUBRISE_ACCOUNT_ID: Optional[str] = None 
    HUBRISE_LOCATION_ID: Optional[str] = None 
    HUBRISE_CATALOG_ID: Optional[str] = None 

    # Postcodes.io API configuration
    POSTCODES_BASE_URL: str = "https://api.postcodes.io"
    POSTCODE_TTL_SECONDS: int = 86400  # 24 hours cache
    HTTP_TIMEOUT_SECONDS: int = 6

    class Config:
        env_file = Path(__file__).parent.parent / ".env"
        extra = 'ignore'

settings = Settings()
