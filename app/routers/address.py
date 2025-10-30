from fastapi import APIRouter, Depends, Query, HTTPException, status 
from app.services.address import AddressService 
from app.core.deps import get_address_service 
from app.schemas.address import Address 

router = APIRouter(prefix="v1//address", tags=["address"])

@router.get("/suggest", response_model=list[Address])
async def suggest(
    query: str = Query(..., min_length=2),
    country: str = "DE",
    limit: int = 20, 
    svc: AddressService = Depends(get_address_service)
):
    items = await svc.suggest(query=query, country=country, limit=limit)
    return items
