import pytest 
from fastapi import FastAPI 
from fastapi.testclient import TestClient 
from app.routers.ultimago import router, get_ultimago_service 
from app.services.ultimago import UltimagoService 
from app.schemas.ultimago import StoreProfile 

class FakeUltimagoService:
    async def get_store_profile(self, store_id: str) -> StoreProfile:
        return StoreProfile(
            StoreURL = "https://dev.tgfpizza.com"
        )

def create_app():
    app = FastAPI()
    app.dependency_overrides[get_ultimago_service] = lambda: FakeUltimagoService()
    app.include_router(router)
    return app 

def test_store_profile_route_happy_path():
    app = create_app()
    client = TestClient(app)
    r = client.get("/ultimago/store-profile", params={"store_id": "DEVDATA"})
    assert r.status_code == 200 
    data = r.json()
    assert data["StoreURL"] == "https://dev.tgfpizza.com"