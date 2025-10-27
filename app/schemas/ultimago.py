from pydantic import BaseModel 

class StoreProfile(BaseModel):
    StoreURL: str
    DeDataSourceName: str

class MenuSRV(BaseModel):
    MenuSRV: str 