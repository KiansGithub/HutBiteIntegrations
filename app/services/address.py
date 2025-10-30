import re 
import httpx 
from fastapi import HTTPException, status 
from app.core.config import settings 
from app.schemas.address import AddressSuggestion 

ADDRESSY_URL = "https://api.addressy.com/Capture/Interactive/Find/v1.10/json3.ws"

class AddressService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.enabled = bool(settings.ADDRESSY_API_KEY)
        self.key = settings.ADDRESSY_API_KEY
    
    def _map_item(self, it: dict) -> AddressSuggestion | None:
        if it.get("Type") != "Address":
            return None 
        text = (it.get("Text") or "").strip()
        desc = (it.get("Description") or "").strip()
        m = re.match(r"^(\d{5})\s+(.+)$", desc)
        postal, city = (m.group(1), m.group(2).strip()) if m else ("", desc)
        return AddressSuggestion(
            id=it.get("Id"),
            label=text, 
            description=desc or None, 
            address=text, 
            city=city, 
            postalCode=postal,
            countryCode="DE",
            formatted=f"{text}, {postal} {city}, DE".strip(", "),
        )

        async def suggest(self, *, query: str, country: str = "DE", limit: int = 20):
            if not self.enabled:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Addressy API key not configured"
                )
            try:
                resp = await self.client.get(
                    ADDRESSY_URL, 
                    params={"Key": self.key, "Text": query, "Countries": country, "Limit": str(limit) },
                    headers={"Accept": "application/json"}, 
                    timeout=5.0
                )
                resp.raise_for_status()
                data = resp.json() or {}
            except Exception as e:
                raise HTTPException(
                    status_code=502, 
                    detail="Address provider error"
                )

            items = data.get("Items") or []
            return [m for it in items if (m := self._map_item(it))]