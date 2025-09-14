import httpx 
from typing import Any, Dict, Optional, Mapping 
from app.core.config import settings 

class HubRiseClient: 
    def __init__(self, access_token: str): 
        self._token = access_token 
        self._base = str(settings.HUBRISE_API_URL)
    
    def headers(self, extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
        base = {"X-Access-Token": self._token, "Content-Type": "application/json"}
        return {**base, **(extra or {})}
    
    async def request(self, method: str, path: str, **kwargs) -> httpx.Response: 
        url = f"{self._base}{path}"
        async with httpx.AsyncClient(timeout=20) as c: 
            resp = await c.request(method, url, headers=self._headers(kwargs.pop("headers", None)))
        # Raise for non-2xx; our exception handler will shape the response 
        resp.raise_for_status()
        return resp 

    # --- Orders: 
    async def create_order(self, location_id: str, order: Dict[str, Any]) => Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}"
        resp = await self._request("GET", path)
        return resp.json()
    
    async def list_orders(
        self,
        location_id: Optional[str] = None,
        account_id: Optional[str] = None,
        params: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, Any]:
        if location_id:
            path = f"/locations/{location_id}/orders"
        elif account_id:
            path = f"/accounts/{account_id}/orders"
        else:
            raise ValueError("location_id or account_id required")

        resp = await self._request("GET", path, params=params)
        return resp.json()

    async def update_order(self, location_id: str, order_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}"
        resp = await self._request("PATCH", path, json=patch)
        return resp.json()