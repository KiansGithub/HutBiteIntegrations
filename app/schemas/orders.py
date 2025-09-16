from __future__ import annotations
from typing import Optional, List, Dict, Union, Literal, Any
from pydantic import BaseModel, model_validator, ConfigDict
from enum import Enum

# HubRise expects money fields as string like "8.50 GBP"
Money = str
# Quantities can be numeric or string, we’ll normalise before sending
DecimalLike = Union[str, int, float]

class OrderStatus(str, Enum):
    new = "new"
    received = "received"
    accepted = "accepted"
    in_preparation = "in_preparation"
    awaiting_shipment = "awaiting_shipment"
    awaiting_collection = "awaiting_collection"
    in_delivery = "in_delivery"
    completed = "completed"
    rejected = "rejected"
    cancelled = "cancelled"
    delivery_failed = "delivery_failed"

class ServiceType(str, Enum):
    delivery = "delivery"
    collection = "collection"
    eat_in = "eat_in"

# ----- Base -----
class HubBase(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        str_strip_whitespace=True,
    )

# ----- Customer -----
class Customer(HubBase):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[str] = None
    birth_date: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    phone_access_code: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[DecimalLike] = None
    longitude: Optional[DecimalLike] = None
    delivery_notes: Optional[str] = None
    sms_marketing: Optional[bool] = None
    email_marketing: Optional[bool] = None

# ----- Order Items & Options -----
class OrderOption(HubBase):
    option_list_name: str
    name: str
    ref: Optional[str] = None
    price: Optional[Money] = None
    quantity: Optional[int] = 1
    removed: Optional[bool] = None

class DealLine(HubBase):
    deal_key: str
    label: Optional[str] = None
    pricing_effect: Optional[Literal["unchanged", "fixed_price", "price_off", "percentage_off"]] = None
    pricing_value: Optional[Money] = None

class OrderItem(HubBase):
    private_ref: Optional[str] = None
    product_name: str
    sku_name: Optional[str] = None
    sku_ref: Optional[str] = None
    price: Money
    quantity: Union[str, DecimalLike]
    subtotal: Optional[Money] = None
    tax_rate: Optional[DecimalLike] = None
    subset: Optional[str] = None
    customer_notes: Optional[str] = None
    points_earned: Optional[DecimalLike] = None
    points_used: Optional[DecimalLike] = None
    options: Optional[List[OrderOption]] = None
    deal_line: Optional[DealLine] = None
    deleted: Optional[bool] = None

# ----- Deals / Discounts / Charges / Payments / Loyalty -----
OrderDealMap = Dict[str, Dict[str, Optional[str]]]

class OrderDiscount(HubBase):
    private_ref: Optional[str] = None
    name: str
    ref: Optional[str] = None
    price_off: Money
    deleted: Optional[bool] = None

class OrderCharge(HubBase):
    private_ref: Optional[str] = None
    name: str
    ref: Optional[str] = None
    price: Money
    tax_rate: Optional[DecimalLike] = None
    deleted: Optional[bool] = None

class OrderPayment(HubBase):
    private_ref: Optional[str] = None
    name: Optional[str] = None
    ref: Optional[str] = None
    amount: Money
    info: Optional[Dict[str, Any]] = None
    deleted: Optional[bool] = None

class OrderLoyaltyOperation(HubBase):
    ref: Optional[str] = None
    name: Optional[str] = None
    delta: DecimalLike
    reason: Optional[str] = None

# ----- Create & Patch -----
class OrderCreate(HubBase):
    status: OrderStatus

    channel: Optional[str] = None
    ref: Optional[str] = None
    private_ref: Optional[str] = None
    service_type: Optional[ServiceType] = None
    service_type_ref: Optional[str] = None
    expected_time: Optional[str] = None
    confirmed_time: Optional[str] = None
    customer_notes: Optional[str] = None
    seller_notes: Optional[str] = None
    collection_code: Optional[str] = None
    coupon_codes: Optional[List[str]] = None

    items: Optional[List[OrderItem]] = None
    deals: Optional[OrderDealMap] = None
    discounts: Optional[List[OrderDiscount]] = None
    charges: Optional[List[OrderCharge]] = None
    payments: Optional[List[OrderPayment]] = None

    customer_id: Optional[str] = None
    customer_list_id: Optional[str] = None
    customer_private_ref: Optional[str] = None
    customer: Optional[Customer] = None

    loyalty_operations: Optional[List[OrderLoyaltyOperation]] = None
    custom_fields: Optional[Dict[str, Any]] = None

    @model_validator(mode='after')
    def _customer_identity_rule(self) -> 'OrderCreate':
        has_id = bool(self.customer_id)
        has_list_pair = bool(self.customer_list_id and self.customer_private_ref)
        has_guest = bool(self.customer)
        if sum([has_id, has_list_pair, has_guest]) > 1:
            raise ValueError(
                "Provide only one of: customer_id, (customer_list_id + customer_private_ref), or customer."
            )
        return self

class OrderPatch(HubBase):
    status: Optional[OrderStatus] = None
    confirmed_time: Optional[str] = None
    seller_notes: Optional[str] = None
    collection_code: Optional[str] = None
    private_ref: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None

    # element mutations
    items: Optional[List[Dict[str, Any]]] = None
    discounts: Optional[List[Dict[str, Any]]] = None
    charges: Optional[List[Dict[str, Any]]] = None
    payments: Optional[List[Dict[str, Any]]] = None

# ----- Minimal response (optional) -----
class OrderOut(HubBase):
    id: Optional[str] = None
    location_id: Optional[str] = None
    created_at: Optional[str] = None
    created_by: Optional[str] = None
    connection_name: Optional[str] = None
    total: Optional[Money] = None
    status: Optional[OrderStatus] = None
