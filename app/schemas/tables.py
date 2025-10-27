from pydantic import BaseModel 
from typing import List

class Table(BaseModel):
    id: str 
    name: str 

class Section(BaseModel):
    id: str 
    name: str 
    table: List[Table]