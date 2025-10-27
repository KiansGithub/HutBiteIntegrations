from pydantic import BaseModel 

class StoreProfile(BaseModel):
    StoreURL: str

class MenuSRV(BaseModel):
    MenuSRV: str 