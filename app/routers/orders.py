from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, Any
from app.core.deps import get_access_token, get_location_id, get_hubrise_conn
from app.clients.hubrise import HubRiseClient

router = APIRouter(prefix="/orders", tags=["orders"])

def client(token: str = Depends(get_access_token)) -> HubRiseClient:
    return HubRiseClient(access_token=token)

@router.get("/example")
async def example_location(conn: dict = Depends(get_hubrise_conn)):
    # Useful sanity check endpoint
    return {
        "connected": True,
        "account_id": conn.get("account_id"),
        "location_id": conn.get("location_id"),
        "catalog_id": conn.get("catalog_id"),
        "client": conn.get("state"),  # arbitrary field you saw returned
    }

# 1) Create order (minimal body; pass-through to HubRise)
@router.post("")
async def create_order(
    order_body: Dict[str, Any],
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    """
    Create an order at the current location.
    Send any valid HubRise order JSON. Minimal example:
    {
      "status": "new",
      "customer": {"first_name": "John"},
      "items": [{"product_name": "Margarita", "price": "9.00 EUR", "quantity": "1"}]
    }
    """
    return await hr.create_order(location_id=location_id, order=order_body)

# 2) Retrieve order
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
    location_scope: bool = Query(True, description="If true, list for current location; else account-level."),
    status: Optional[str] = None,
    created_by: Optional[str] = None,
    private_ref: Optional[str] = None,
    after: Optional[str] = None,
    before: Optional[str] = None,
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

# 4) Update order (PATCH)
@router.patch("/{order_id}")
async def update_order(
    order_id: str,
    patch_body: Dict[str, Any],
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    """
    PATCH the order. Ex:
    { "status": "accepted",
      "items": [{ "id": "item-id-from-GET", "deleted": true }],
      "charges": [{ "name": "Delivery", "price": "1.50 EUR" }]
    }
    """
    return await hr.update_order(location_id=location_id, order_id=order_id, patch=patch_body)
