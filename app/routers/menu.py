from fastapi import APIRouter, Depends, HTTPException, status, Query 
from app.services.menu import MenuService 
from app.core.deps import get_menu_service 
from app.schemas.menu import MenuData

router = APIRouter(prefix="/menu", tags=["menu"])

@router.get("/items", response_model=MenuData)
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