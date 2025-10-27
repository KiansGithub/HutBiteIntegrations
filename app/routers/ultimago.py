from fastapi import APIRouter, Depends, Query, HTTPException, status 
from app.schemas.ultimago import StoreProfile 
from app.services.ultimago import UltimagoService 
from app.core.deps import get_ultimago_service

router = APIRouter(prefix="/ultimago", tags=["ultimago"])

@router.get("/store-profile", response_model=StoreProfile)
async def store_profile(
    store_id: str = Query(..., description="Ultimago store ID"),
    svc: UltimagoService = Depends(get_ultimago_service)
):
    return await svc.get_store_profile(store_id)