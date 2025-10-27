import pytest 
from app.services.ultimago import UltimagoService

@pytest.mark.asyncio 
async def test_get_store_profile():
    service = UltimagoService()
    store_id = "DEVDATA"

    result = await service.get_store_profile(store_id)

    # Check shape and type 
    assert result is not None 
    assert hasattr(result, "StoreURL")
    assert result.StoreURL == "https://dev.tgfpizza.com"