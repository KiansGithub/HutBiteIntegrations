from fastapi import APIRouter, Depends, Query, HTTPException, status 
from app.schemas.tables import Section 
from app.services.tables import TableService 
from app.core.deps import get_tables_service 

router = APIRouter(prefix="/tables", tags=["tables"])

@router.get("/sections", response_model=list[Section])
async def get_sections(
    store_id: str = Query(..., description="Store ID"),
    menu_srv: str = Query(..., description="Menu_srv"),
    database_name: str = Query(..., description="Database Name"), 
    svc: TableService = Depends(get_tables_service)
):
    try:
        return await svc.get_sections(store_id, menu_srv, database_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=str(e)
        )