# app/routers/orders.py
from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, Any
from app.core.deps import get_access_token, get_location_id, get_hubrise_conn
from app.clients.hubrise import HubRiseClient
from app.schemas.orders import OrderCreate, OrderPatch  # <-- use schemas

router = APIRouter(prefix="/orders", tags=["orders"])

def client(token: str = Depends(get_access_token)) -> HubRiseClient:
    return HubRiseClient(access_token=token)

@router.get("/example")
async def example_location(conn: dict = Depends(get_hubrise_conn)):
    """Quick sanity check that OAuth/session has HubRise fields."""
    return {
        "connected": True,
        "account_id": conn.get("account_id"),
        "location_id": conn.get("location_id"),
        "catalog_id": conn.get("catalog_id"),
        "client": conn.get("state"),
    }

# 1) Create order (validated by OrderCreate)
@router.post("")
async def create_order(
    payload: OrderCreate,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    """
    Create an order at the current location.
    Send a HubRise-compatible body; we validate core fields & pass through extras.
    """
    body = payload.dict(exclude_none=True)
    return await hr.create_order(location_id=location_id, body=body)

# 2) Retrieve order by id
@router.get("/{order_id}")
async def retrieve_order(
    order_id: str,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.retrieve_order(location_id=location_id, order_id=order_id)

# 3) List orders (location or account scope)
@router.get("")
async def list_orders(
    location_scope: bool = Query(
        True, description="If true, list for current location; if false, list for the whole account."
    ),
    status: Optional[str] = Query(None, description="Filter by status (e.g., accepted)"),
    created_by: Optional[str] = None,
    private_ref: Optional[str] = None,
    after: Optional[str] = Query(None, description="ISO8601 inclusive lower bound"),
    before: Optional[str] = Query(None, description="ISO8601 exclusive upper bound"),
    customer_id: Optional[str] = None,
    location_id: str = Depends(get_location_id),
    conn: dict = Depends(get_hubrise_conn),
    hr: HubRiseClient = Depends(client),
):
    params = {
        k: v for k, v in {
            "status": status,
            "created_by": created_by,
            "private_ref": private_ref,
            "after": after,
            "before": before,
            "customer_id": customer_id,
        }.items() if v is not None
    }

    if location_scope:
        return await hr.list_orders(location_id=location_id, params=params)
    else:
        account_id = conn.get("account_id")
        return await hr.list_orders(account_id=account_id, params=params)

# 4) Update order (PATCH) using OrderPatch
@router.patch("/{order_id}")
async def update_order(
    order_id: str,
    patch: OrderPatch,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    """
    Patch fields HubRise allows (status, confirmed_time, notes, collection_code, private_ref, custom_fields)
    and mutate elements (items/discounts/charges/payments) via id + deleted / add.
    """
    body = patch.dict(exclude_none=True)
    return await hr.update_order(location_id=location_id, order_id=order_id, patch=body)
