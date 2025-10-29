from fastapi import APIRouter, Depends, Query, HTTPException, status 
from app.schemas.ultimago import StoreProfile, MenuSRV, TableBill, TableBillResponse
from app.services.ultimago import UltimagoService
from app.core.deps import get_ultimago_service

router = APIRouter(prefix="/ultimago", tags=["ultimago"])

@router.get("/store-profile", response_model=StoreProfile)
async def store_profile(
    store_id: str = Query(..., description="Ultimago store ID"),
    svc: UltimagoService = Depends(get_ultimago_service)
):
    return await svc.get_store_profile(store_id)

@router.get("/menu-srv", response_model=MenuSRV)
async def menu_srv(
    store_id: str = Query(..., description="Ultimago Store ID"), 
    svc: UltimagoService = Depends(get_ultimago_service)
):
    return await svc.get_menu_srv(store_id)

@router.get("/table-bill", response_model=TableBill)
async def table_bill(
    menu_srv: str = Query(..., description="Ultimago Menu_Srv"), 
    section_name: str = Query(..., description="Ultimago section name"), 
    table_name: str = Query(..., description="Ultimago table name"), 
    svc: UltimagoService = Depends(get_ultimago_service)
):
    return await svc.get_table_bill(menu_srv, section_name, table_name)

@router.post("/settle-table-bill", response_model=TableBillResponse)
async def settle_table_bill(
    menu_srv: str = Query(..., description="Ultimago menusrv"), 
    order_id: int = Query(..., description="Order ID"), 
    svc: UltimagoService = Depends(get_ultimago_service)
):
    return await svc.settle_table_bill(menu_srv, order_id)