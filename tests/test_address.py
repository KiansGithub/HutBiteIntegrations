import pytest 
from app.services.address import AddressService 
import httpx 

@pytest.mark.asyncio 
async def test_suggest():
    http_client = httpx.AsyncClient()
    service = AddressService(http_client=http_client)
    query = "70173 3 sch"
    country = "DE"
    limit = 20 

    result = await service.suggest(query=query, country=country, limit=limit)
    assert result is not None 
    assert len(result) > 0