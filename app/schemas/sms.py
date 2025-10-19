from pydantic import BaseModel, Field 
from typing import Optional 
from enum import Enum 

class SMSStatus(str, Enum):
    success = "success"
    error = "error"
    disabled = "disabled"

class OrderSMSRequest (BaseModel): 
    restaurant_name: str = Field(..., description="Name of the restaurant")
    customer_name: str = Field(..., description="Name of the customer")
    customer_phone: str = Field(..., description="Customer Phone Number")
    order_amount: str = Field(..., description="Order Amount for customer")
    order_ref: Optional[str] = Field(None, description="Order Reference")

class SMSResponse(BaseModel):
    status: SMSStatus 
    message: str 
    sid: Optional[str] = None 
    error_code: Optional[Union[int, str]] = None 

class SMSTestRequest(BaseModel):
    phone_number: str = Field(..., description="Phone number to send test SMS")
    message: str = Field(..., description="Test message content")