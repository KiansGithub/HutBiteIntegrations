import json 
import httpx 
from fastapi import HTTPException, status 
import base64 
import logging 
from typing import List 
from pydantic import TypeAdapter 
from json import JSONDecodeError
from app.schemas.tables import Section 
from app.core.config import settings 

logger = logging.getLogger(__name__)


class TableService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client 
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
        
    async def get_sections(
        self, 
        store_id: str, 
        menu_srv: str, 
        database_name: str 
    ) -> List[Section]:
        if not self.enabled:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                detail="Ultima credentials not configured"
            )
        try:
            resp = await self.client.get(
                f"{menu_srv}/Tables", 
                params={
                    "StoreID": store_id, 
                    "DataBaseName": database_name
                },
                headers={
                    "Authorization": self.auth_header, 
                    "Accept": "application/json"
                },
            )
            resp.raise_for_status()

            logger.info(f"Sections retrieved successfully for store ID: {store_id}")
            outer = resp.json()
            raw_inner = outer.get("WinPizzaObject")

            if not raw_inner:
                return []
            
            try:
                inner = json.loads(raw_inner)
            except JSONDecodeError as e:
                raise HTTPException(
                    status_code=502, 
                    detail="Failed to decode JSON response from Ultima"
                )
            
            sections = inner
            return sections
        
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to retrieve sections"
            )