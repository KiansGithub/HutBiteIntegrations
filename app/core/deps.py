from fastapi import Depends, HTTPException, Request 
from .config import settings 

def get_hubrise_conn(request: Request) -> dict: 
    conn = request.session.get("hubrise_conn")
    if not conn:
        raise HTTPException(status_code=401, detail="Not connected to HubRise")
    return conn 

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