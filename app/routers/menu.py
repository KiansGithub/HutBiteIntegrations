from fastapi import APIRouter, Depends, HTTPException, status 
from app.services.menu_service import MenuService 
from app.core.deps import get_menu_service 
from app.schemas.menu import Categories
from typing import List

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("/items", response_model=List[Categories])
async def get_menu_items(
    store_id: str = Query(..., description="Store ID"),
    svc: MenuService = Depends(get_menu_service)
):
    try:
        return await svc.get_menu_items(store_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )