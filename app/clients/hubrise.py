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
            resp = await c.request(method, url, headers=self.headers(kwargs.pop("headers", None)), **kwargs)
        # Raise for non-2xx; our exception handler will shape the response 
        resp.raise_for_status()
        return resp 

    # --- Orders: 
    async def create_order(self, location_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders"
        resp = await self.request("POST", path, json=body)
        return resp.json()
    
    # retrieve order 
    async def retrieve_order(self, location_id: str, order_id: str) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}"
        resp = await self.request("GET", path)
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

        resp = await self.request("GET", path, params=params)
        return resp.json()

    async def update_order(self, location_id: str, order_id: str, patch: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}"
        resp = await self.request("PATCH", path, json=patch)
        return resp.json()
    
    # --- Delivery Quotes 
    async def create_delivery_quote(self, location_id: str, order_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}/delivery_quotes"
        resp = await self.request("POST", path, json=body)
        return resp.json()
    
    async def accept_delivery_quote(self, location_id: str, order_id: str, quote_id: str) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}/delivery_quotes/{quote_id}/accept"
        resp = await self.request("POST", path)
        return resp.json()
    
    # --- Deliveries 
    async def create_delivery(self, location_id: str, order_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}/delivery"
        resp = await self.request("POST", path, json=body)
        return resp.json()

    async def retrieve_delivery(self, location_id: str, order_id: str) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}/delivery"
        resp = await self.request("GET", path)
        return resp.json()

    async def update_delivery(self, location_id: str, order_id: str, body: Dict[str, Any]) -> Dict[str, Any]:
        path = f"/locations/{location_id}/orders/{order_id}/delivery"
        resp = await self.request("PATCH", path, json=body)
        return resp.json()
    
    async def get_catalog(self, catalog_id: str) -> Dict[str, Any]:
        path = f"/catalogs/{catalog_id}"
        resp = await self.request("GET", path)
        return resp.json()
    
    # --- Locations (for opening hours, etc.) ---
    async def get_location(self, location_id: str) -> Dict[str, Any]:
        path = f"/locations/{location_id}"
        resp = await self.request("GET", path)
        return resp.json()
    

