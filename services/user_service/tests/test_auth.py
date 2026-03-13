import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_register():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/users/register", json={
            "email": "test@example.com",
            "password": "secret",
            "full_name": "Test User",
            "role": "driver"
        })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"