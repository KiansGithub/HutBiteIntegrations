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
