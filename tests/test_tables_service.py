import pytest 
from app.services.tables import TableService 
import httpx 

@pytest.mark.asyncio 
async def test_get_sections():
    http_client = httpx.AsyncClient()
    service = TableService(http_client=http_client)
    store_id = "DEVDATA"
    menu_srv = "http://services.tgfpizza.com/WinPizzaMainServices/WinPizzaService20014.WebSubmitOrder.svc"
    database_name="testdata"

    result = await service.get_sections(store_id, menu_srv, database_name)

    assert result is not None 
    assert len(result) > 0 
    