from pydantic import BaseModel 

class Table(BaseModel):
    id: str 
    name: str 

class Section(BaseModel):
    id: str 
    name: str 
    table: Table[]