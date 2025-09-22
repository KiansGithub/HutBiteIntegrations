from typing import Optional, Dict, Any 
from datetime import datetime 
from sqlmodel import Field, SQLModel, JSON 

class StoreConnection(SQLModel, table=True): 
    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str = Field(index=True, unique=True)
    access_token: str 
    account_id: str 
    location_id: str 
    catalog_id: Optional[str] = None 
    user_id: Optional[str] = None 
    account_name: Optional[str] = None 
    location_name: Optional[str] = None 
    catalog_name: Optional[str] = None 
    raw_payload: Optional[Dict[str, Any]] = Field(default=None, sa_column_kwargs)={"type_": JSON}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

