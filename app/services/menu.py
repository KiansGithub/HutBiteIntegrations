from fastapi import HTTPException, status 
from app.data.menus import MENU_ELCURIOSO

class MenuService:
    
    async def get_menu_items(
        self, 
        store_id: str
    ):
        # TODO: implement dynamic menu retrieval
        return MENU_ELCURIOSO
