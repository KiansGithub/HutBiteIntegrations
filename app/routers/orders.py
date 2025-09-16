from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from typing import Optional, Dict, Any
from decimal import Decimal, InvalidOperation
import re
import httpx
from fastapi import HTTPException
import logging

from app.core.deps import get_access_token, get_location_id, get_hubrise_conn
from app.clients.hubrise import HubRiseClient
from app.schemas.orders import OrderCreate, OrderPatch

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orders", tags=["orders"])

def client(token: str = Depends(get_access_token)) -> HubRiseClient:
    return HubRiseClient(access_token=token)

# --- helpers for HubRise formatting ---
CURRENCY = "GBP"  # optionally derive from location via hr.get_location(...)

# e.g. "8.50 GBP" or "10 GBP" (2dp optional)
_MONEY_WITH_CURRENCY = re.compile(r"^\s*-?\d+(?:\.\d{1,2})?\s+[A-Z]{3}\s*$")

def _fmt_money(v, currency: str = CURRENCY) -> Optional[str]:
    if v is None:
        return None
    s = str(v).strip()
    # keep if already formatted like "8.50 GBP"
    if _MONEY_WITH_CURRENCY.match(s):
        return s
    try:
        q = Decimal(s)
    except InvalidOperation:
        # pass through; HubRise will surface a precise error if bad
        return s
    return f"{q.quantize(Decimal('0.01'))} {currency}"

def _fmt_decimal_string(v) -> Optional[str]:
    return None if v is None else str(v)

def _normalise_order_for_hubrise(body: dict, currency: str = CURRENCY) -> dict:
    b = dict(body)

    # TOP-LEVEL TOTAL
    if "total" in b and b["total"] is not None:
        b["total"] = _fmt_money(b["total"], currency)

    # items
    items = []
    for it in b.get("items", []) or []:
        it = dict(it)
        it["price"] = _fmt_money(it.get("price"), currency)
        if it.get("subtotal") is not None:
            it["subtotal"] = _fmt_money(it.get("subtotal"), currency)
        it["quantity"] = _fmt_decimal_string(it.get("quantity"))

        # options
        opts = []
        for op in it.get("options", []) or []:
            op = dict(op)
            if op.get("price") is not None:
                op["price"] = _fmt_money(op["price"], currency)
            if op.get("quantity") is not None:
                # HubRise expects options.quantity as integer
                op["quantity"] = int(op["quantity"])
            opts.append(op)
        it["options"] = opts or None

        items.append(it)
    b["items"] = items or None

    # charges
    charges = []
    for ch in b.get("charges", []) or []:
        ch = dict(ch)
        ch["price"] = _fmt_money(ch.get("price"), currency)
        charges.append(ch)
    b["charges"] = charges or []

    # discounts
    discounts = []
    for d in b.get("discounts", []) or []:
        d = dict(d)
        d["price_off"] = _fmt_money(d.get("price_off"), currency)
        discounts.append(d)
    b["discounts"] = discounts or []

    # payments
    pays = []
    for p in b.get("payments", []) or []:
        p = dict(p)
        p["amount"] = _fmt_money(p.get("amount"), currency)
        pays.append(p)
    b["payments"] = pays or None

    return b

# --- endpoints ---

@router.get("/example", response_model=None)
async def example_location(conn: dict = Depends(get_hubrise_conn)) -> dict:
    return {
        "connected": True,
        "account_id": conn.get("account_id"),
        "location_id": conn.get("location_id"),
        "catalog_id": conn.get("catalog_id"),
        "client": conn.get("state"),
    }

@router.post("")
async def create_order(
    payload: OrderCreate,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    body = jsonable_encoder(payload, exclude_none=True)
    body = _normalise_order_for_hubrise(body, currency=CURRENCY)
    
    try:
        resp = await hr.create_order(location_id=location_id, body=body)
        return resp 
    except httpx.HTTPStatusError as e: 
        # HubRise error details 
        status = e.response.status_code 
        try:
            detail = e.response.json()
        except Exception:
            detail = {"error": e.response.text}
        logger.error("HubRise %s: %s", status, detail)
        raise HTTPException(status_code=status, detail=detail)
    except Exception as e:
        logger.exception("Create order failed")
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/{order_id}")
async def retrieve_order(
    order_id: str,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.retrieve_order(location_id=location_id, order_id=order_id)

@router.get("")
async def list_orders(
    location_scope: bool = Query(True, description="If true, list for current location; if false, list for the whole account."),
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
    params = {k: v for k, v in {
        "status": status,
        "created_by": created_by,
        "private_ref": private_ref,
        "after": after,
        "before": before,
        "customer_id": customer_id,
    }.items() if v is not None}

    if location_scope:
        return await hr.list_orders(location_id=location_id, params=params)
    else:
        account_id = conn.get("account_id")
        return await hr.list_orders(account_id=account_id, params=params)

@router.patch("/{order_id}")
async def update_order(
    order_id: str,
    patch: OrderPatch,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    body = jsonable_encoder(patch, exclude_none=True)
    body = _normalise_order_for_hubrise(body, currency=CURRENCY)
    return await hr.update_order(location_id=location_id, order_id=order_id, patch=body)
