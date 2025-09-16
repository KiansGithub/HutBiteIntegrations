from fastapi import APIRouter, Depends
from app.core.deps import get_location_id, get_access_token
from app.clients.hubrise import HubRiseClient
from app.schemas.deliveries import (
    DeliveryQuoteCreate,
    DeliveryQuoteOut,
    DeliveryCreate,
    DeliveryOut,
)

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

def client(token: str = Depends(get_access_token)) -> HubRiseClient:
    return HubRiseClient(access_token=token)

# 1. Create a delivery quote
@router.post("/orders/{order_id}/quotes", response_model=DeliveryQuoteOut, status_code=201)
async def create_quote(
    order_id: str,
    body: DeliveryQuoteCreate,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.create_delivery_quote(location_id, order_id, body.dict(exclude_none=True))

# 2. Accept a delivery quote
@router.post("/orders/{order_id}/quotes/{quote_id}/accept", status_code=200)
async def accept_quote(
    order_id: str,
    quote_id: str,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.accept_delivery_quote(location_id, order_id, quote_id)

# 3. Create a delivery
@router.post("/orders/{order_id}", response_model=DeliveryOut, status_code=201)
async def create_delivery(
    order_id: str,
    body: DeliveryCreate,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.create_delivery(location_id, order_id, body.dict(exclude_none=True))

# 4. Retrieve delivery
@router.get("/orders/{order_id}", response_model=DeliveryOut)
async def retrieve_delivery(
    order_id: str,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.retrieve_delivery(location_id, order_id)

# 5. Update delivery
@router.patch("/orders/{order_id}", response_model=DeliveryOut)
async def update_delivery(
    order_id: str,
    body: DeliveryCreate,
    location_id: str = Depends(get_location_id),
    hr: HubRiseClient = Depends(client),
):
    return await hr.update_delivery(location_id, order_id, body.dict(exclude_none=True))
