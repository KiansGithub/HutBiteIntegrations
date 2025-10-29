from pydantic import BaseModel 

class StoreProfile(BaseModel):
    StoreURL: str
    DeDataSourceName: str

class MenuSRV(BaseModel):
    MenuSRV: str 

class TableBill(BaseModel):
    order_id: int 
    items: List[Item] 
    total_amount: float

class Item(BaseModel):
    name: str 
    quantity: int 
    price: float 