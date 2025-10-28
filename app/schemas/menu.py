from typing import List, Optional 
from pydantic import BaseModel 

class VideoItem(BaseModel):
    id: str 
    title: str 
    videoUrl: str 

class Category(BaseModel):
    id: str 
    name: str 
    items: List[VideoItem]

class MenuData(BaseModel):
    categories: List[Category]