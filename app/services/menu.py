from fastapi import HTTPException, status 
from app.data.menus import MENU_ELCURIOSO

class MenuService:

    def __init__(self, http_client: httpx.AsyncClient):
        self.http_client = http_client
    
    async def get_menu_items(
        self, 
        store_id: str
    ):
        # TODO: implement dynamic menu retrieval
        return MENU_ELCURIOSO
