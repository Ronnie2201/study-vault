import pytest
from httpx import ASGITransport, AsyncClient

from app.main import create_application


@pytest.fixture
def app():
    """Create a fresh app instance for each test"""
    return create_application()


@pytest.mark.asyncio
async def test_health_endpoint(app):
    """Test that the health endpoint returns 200 OK."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "database" in data
        assert data["version"] == "0.1.0"
