from pydantic import BaseModel 
from typing import List
from pydantic import Field 

class Table(BaseModel):
    id: int
    name: str = Field(alias="Name")

class Section(BaseModel):
    id: int 
    name: str = Field(alias="Name")
    tables: List[Table]

class UltimagoTableResponse(BaseModel):
    DataObject: None 
    DeMsgBody: None 
    DeMsgType: int 
    WinPizzaObject: List[Section]
    