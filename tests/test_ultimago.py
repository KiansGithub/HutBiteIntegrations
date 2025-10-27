import pytest 
from app.services.ultimago import UltimagoService
import httpx

@pytest.mark.asyncio 
async def test_get_store_profile():
    http_client = httpx.AsyncClient()
    service = UltimagoService(http_client=http_client)
    store_id = "DEVDATA"

    result = await service.get_store_profile(store_id)

    # Check shape and type 
    assert result is not None 
    assert hasattr(result, "StoreURL")
    assert result.StoreURL == "https://dev.tgfpizza.com"

    await http_client.aclose()

@pytest.mark.asyncio 
async def test_get_menu_srv():
    http_client = httpx.AsyncClient()
    service = UltimagoService(http_client=http_client)
    store_id = "DEVDATA"

    result = await service.get_menu_srv(store_id)

    assert result is not None 
    assert hasattr(result, "MenuSRV")
    assert result.MenuSRV == "http://Services.tgfpizza.com/WinPizzaMainServices/WinPizzaService20014.WebSubmitOrder.svc"