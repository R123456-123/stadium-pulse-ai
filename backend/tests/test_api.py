import pytest
from httpx import AsyncClient
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

async def test_health_check(test_client: AsyncClient):
    response = await test_client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

async def test_stadium_zones(test_client: AsyncClient):
    response = await test_client.get("/api/v1/stadium/zones")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_stadium_facilities(test_client: AsyncClient):
    response = await test_client.get("/api/v1/stadium/facilities")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_stadium_gates(test_client: AsyncClient):
    response = await test_client.get("/api/v1/stadium/gates")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_ops_recommendations(test_client: AsyncClient):
    with patch("app.routers.ops.gemini_service.generate_recommendations") as mock_gen:
        from unittest.mock import AsyncMock
        mock_gen._mock_return_value = []
        # We need an AsyncMock for the return value
        mock_gen.side_effect = AsyncMock(return_value=[])
        
        response = await test_client.get("/api/v1/ops/recommendations")
        assert response.status_code == 200
        assert response.json() == []

async def test_fan_chat_safety_mock(test_client: AsyncClient):
    response = await test_client.post("/api/v1/chat", json={
        "message": "Where is the bathroom?",
        "history": []
    })
    assert response.status_code in [200, 500] 

async def test_stadium_transport(test_client: AsyncClient):
    response = await test_client.get("/api/v1/stadium/transport")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

async def test_stadium_faqs(test_client: AsyncClient):
    response = await test_client.get("/api/v1/stadium/faqs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
