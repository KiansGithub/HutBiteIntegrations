from fastapi import Depends, HTTPException, Request 
import httpx
from .config import settings 
from app.services.ultimago import UltimagoService 
from app.services.tables import TableService
from app.services.menu import MenuService

def get_hubrise_conn(request: Request) -> dict: 
    # 1) Session (if present)
    if request: 
        sess = request.session.get("hubrise_conn")
        if sess: 
            return sess 
        
    # 2) Env fallback (token mode)
    if settings.HUBRISE_ACCESS_TOKEN and settings.HUBRISE_LOCATION_ID: 
        return {
            "access_token": settings.HUBRISE_ACCESS_TOKEN, 
            "account_id": settings.HUBRISE_ACCOUNT_ID, 
            "location_id": settings.HUBRISE_LOCATION_ID, 
            "catalog_id": settings.HUBRISE_CATALOG_ID, 
        }
    
    # Neither session nor env configured 
    raise HTTPException(status_code=401, detail="Not connected to HubRise")

def get_access_token(conn: dict = Depends(get_hubrise_conn)) -> str: 
    token = conn.get("access_token")
    if not token: 
        raise HTTPException(status_code=401, detail="Missing HubRise access token")
    return token 

def get_location_id(request: Request, conn: dict = Depends(get_hubrise_conn)) -> str: 
    # Prefer the location from session; fallback to env efault 
    loc = conn.get("location_id") or settings.DEFAULT_LOCATION_ID 
    if not loc: 
        raise HTTPException(status_code=400, detail="No HubRise location_id available")
    return loc

# ---- NEW: Shared HTTP Client 
def get_http_client(request: Request) -> httpx.AsyncClient: 
    """
    Return the ONE shared httpx.AsyncClient created in app.main lifespan 
    This enables connection pooling and avoids creating a client per request. 
    """
    client = getattr(request.app.state, "http_client", None)
    if client is None: 
        # If this ever triggers, the app didn't create the client in main.py lifespan 
        raise HTTPException(status_code=500, detail="HTTP client not initialized")
    return client

# ---- Ultimago Service 
def get_ultimago_service(client: httpx.AsyncClient = Depends(get_http_client)) -> UltimagoService:
    return UltimagoService(http_client=client)

def get_tables_service(client: httpx.AsyncClient = Depends(get_http_client)) -> TableService:
    return TableService(http_client=client) 

def get_menu_service(client: httpx.AsyncClient = Depends(get_http_client)) -> MenuService:
    return MenuService(http_client=client)