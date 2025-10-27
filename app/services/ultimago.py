import httpx 
from app.schemas.ultimago import StoreProfile 
from fastapi import HTTPException, status 
from app.core.config import settings 
import base64 

ULTIMAGO_BASE_URL = "https://services.tgfpizza.com/ThirdPartyServices/StoreServices.svc/"

class UltimagoService:
    def __init__(self):
        self.enabled = bool(
            settings.ULTIMAGO_USERNAME and 
            settings.ULTIMAGO_PASSWORD
        )

        if self.enabled:
            self.auth_header = "Basic " + base64.b64encode(
                f"{settings.ULTIMAGO_USERNAME}:{settings.ULTIMAGO_PASSWORD}".encode()
            ).decode()
        else:
            self.auth_header = None 

    async def get_store_profile(self, store_id: str) -> StoreProfile: 

        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Ultima credentials not configured"
            )
        try:

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(
                    f"{ULTIMAGO_BASE_URL}GetStoreProfile/{store_id}",
                    headers={
                        "Authorization": self.auth_header, 
                        "Content-Type": "application/json",
                    },
                )
            resp.raise_for_status()

            store_profile = StoreProfile(**resp.json())
            return store_profile
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to retrieve store profile"
            )