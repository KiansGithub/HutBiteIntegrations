import asyncio, random, httpx 
from typing import Any, Dict, Optional, Mapping, Iterable
from app.core.config import settings 

_RETRY_STATUSES: set[int] = {429, 500, 502, 503, 504}

class HubRiseClient: 
    def __init__(self, access_token: str, http: httpx.AsyncClient): 
        self._token = access_token 
        self._base = str(settings.HUBRISE_API_URL)
        self._http = http 
    
    def headers(self, extra: Optional[Mapping[str, str]] = None) -> Dict[str, str]:
        base = {"X-Access-Token": self._token, 
                "Content-Type": "application/json", 
                "User-Agent": "hutbite-backend/1.0"
                }
        return {**base, **(extra or {})}
    
    async def _request_with_retries(
        self, method: str, path: str, *, max_attempts: int = 3, backoff_base: float = 0.25,
        retry_statuses: Iterable[int] = _RETRY_STATUSES, **kwargs
    ) -> httpx.Response: 
        url = f"{self._base}{path}"
        headers = self.headers(kwargs.pop("headers", None))
        attempt = 0
        while True: 
            attempt += 1
            try:
                resp = await self._http.request(method, url, headers=headers, **kwargs)
                if resp.status_code in retry_statuses and attempt < max_attempts: 
                    ra = resp.headers.get("Retry-After")
                    delay = float(ra) if (ra and ra.isdigit()) else (backoff_base * (2 ** (attempt-1)) + random.uniform(0, 0.2))
                    await asyncio.sleep(delay)
                    continue 
                resp.raise_for_status()
                return resp 
            
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.TransportError):
                if attempt >= max_attempts: raise 
                delay = backoff_base * (2 ** (attempt - 1)) + random.uniform(0, 0.2)
                await asyncio.sleep(delay)
    
    async def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        return await self._request_with_retries(method, path, **kwargs)

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
    

