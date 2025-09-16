from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_access_token, get_hubrise_conn, get_location_id 
from app.clients.hubrise import HubRiseClient 

router = APIRouter(prefix="/catalog", tags=["catalog"])

def client(token: str = Depends(get_access_token)) -> HubRiseClient: 
    return HubRiseClient(access_token=token)

@router.get("")
async def get_full_catalog(
    conn: dict = Depends(get_hubrise_conn), 
    hr: HubRiseClient = Depends(client),
): 
    """
    Return the entire Hubrise catalog for the connected session. 
    This uses the recommended single-call endpoint: GET / catalogs/:id 
    """
    catalog_id = conn.get("catalog_id")
    if not catalog_id: 
        raise HTTPException(status_code=400, detail="No catalog_id in session.")
    return await hr.get_catalog(catalog_id)

@router.get("/hours")
async def get_opening_hours(
    location_id: str = Depends(get_location_id), 
    hr: HubRiseClient = Depends(client), 
):
    """
    Returns the location object; frontend can read opening_hours, cutoff_time, etc.
    """
    loc = await hr.get_location(location_id)
    return {
        "id": loc.get("id"), 
        "name": loc.get("name"), 
        "timezone": loc.get("timezone"), 
        "opening_hours": loc.get("opening_hours"), 
        "cutoff_time": loc.get("cutoff_time"), 
        "address": {
            "address": loc.get("address"), 
            "postal_code": loc.get("postal_code"), 
            "city": loc.get("city"), 
            "country": loc.get("country"), 
        }, 
        "custom_fields": loc.get("custom_fields"),
    }