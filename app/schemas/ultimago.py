from pydantic import BaseModel 
from typing import List 

class StoreProfile(BaseModel):
    StoreURL: str
    DeDataSourceName: str

class MenuSRV(BaseModel):
    MenuSRV: str 

class Item(BaseModel):
    name: str 
    quantity: int 
    price: float 

class TableBill(BaseModel):
    order_id: int 
    items: List[Item] 
    total_amount: float