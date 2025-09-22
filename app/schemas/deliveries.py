from typing import Optional 
from pydantic import BaseModel 
from enum import Enum 

# ----- Delivery Status -----
class DeliveryStatus(str, Enum):
    pending = "pending"
    pickup_enroute = "pickup_enroute"
    pickup_approaching = "pickup_approaching"
    pickup_waiting = "pickup_waiting"
    dropoff_enroute = "dropoff_enroute"
    dropoff_approaching = "dropoff_approaching"
    dropoff_waiting = "dropoff_waiting"
    delivered = "delivered"
    cancelled = "cancelled"

# ----- Delivery Quotes -----
class DeliveryQuoteCreate(BaseModel):
    carrier: str 
    fee: str 
    carrier_ref: Optional[str] = None 
    ref: Optional[str] = None 
    estimated_pickup_at: Optional[str] = None 
    estimated_dropoff_at: Optional[str] = None 

class DeliveryQuoteOut(DeliveryQuoteCreate):
    id: str 
    order_id: str 
    location_id: str 
    accepted_at: Optional[str] = None 

# ----- Deliveries -----
class DeliveryCreate(BaseModel):
    carrier: str 
    status: DeliveryStatus 
    carrier_ref: Optional[str] = None 
    ref: Optional[str] = None 
    fee: Optional[str] = None 
    estimated_pickup_at: Optional[str] = None 
    estimated_dropoff_at: Optional[str] = None 
    tracking_url: Optional[str] = None 
    driver_pickup_url: Optional[str] = None 
    driver_name: Optional[str] = None 
    driver_phone: Optional[str] = None 
    driver_phone_access_code: Optional[str] = None 
    driver_latitude: Optional[float] = None 
    driver_longitude: Optional[float] = None 

class DeliveryOut(DeliveryCreate):
    order_id: str 
    location_id: str 
    assigned_at: Optional[str] = None 
    pickup_at: Optional[str] = None 
    delivered_at: Optional[str] = None 
    cancelled_at: Optional[str] = None 
