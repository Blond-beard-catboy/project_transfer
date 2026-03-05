import httpx
from app.core.config import get_settings

settings = get_settings()

async def get_cargo(cargo_id: int, headers: dict = None):
    """Запрашивает данные груза из Cargo Service."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.CARGO_SERVICE_URL}/api/cargo/{cargo_id}",
            headers=headers or {}
        )
        resp.raise_for_status()
        return resp.json()