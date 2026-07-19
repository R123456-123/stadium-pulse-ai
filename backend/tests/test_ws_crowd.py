import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.ws_crowd import manager

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_broadcast():
    with client.websocket_connect("/api/v1/ws/crowd") as websocket:
        # Simulate a broadcast from the background task
        test_data = {"zones": [{"name": "Test Zone", "current_occupancy": 100, "capacity": 200}]}
        
        # We need to run broadcast in an asyncio event loop, but TestClient websocket is synchronous.
        # Actually since we are in async context we can await broadcast
        await manager.broadcast(test_data)
        
        data = websocket.receive_json()
        assert "zones" in data
        assert data["zones"][0]["name"] == "Test Zone"
        
        # Test client disconnect
        websocket.close()
