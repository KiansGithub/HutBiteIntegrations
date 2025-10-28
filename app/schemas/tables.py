from pydantic import BaseModel 
from typing import List

class Table(BaseModel):
    id: str 
    name: str 

class Section(BaseModel):
    id: str 
    name: str 
    tables: List[Table]

class UltimagoTableResponse(BaseModel):
    DataObject: None 
    DeMsgBody: None 
    DeMsgType: int 
    WinPizzaObject: List[Section]
    