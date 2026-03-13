import httpx
from app.core.config import get_settings

settings = get_settings()

async def import_cargo_to_cargo_service(cargo_data: dict, headers: dict = None) -> dict:
    """Отправляет данные груза в Cargo Service для создания."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.CARGO_SERVICE_URL}/api/cargo/",
            json=cargo_data,
            headers=headers or {}
        )
        resp.raise_for_status()
        return resp.json()