import httpx
from app.core.config import get_settings

settings = get_settings()

async def create_route_for_cargo(cargo_id: int, headers: dict = None):
    """Создаёт маршрут и добавляет в него груз, возвращает route_id."""
    async with httpx.AsyncClient() as client:
        # 1. Создаём пустой маршрут
        resp = await client.post(
            f"{settings.ROUTE_SERVICE_URL}/api/routes/",
            json={},
            headers=headers or {}
        )
        resp.raise_for_status()
        route = resp.json()
        route_id = route["id"]

        # 2. Добавляем груз в маршрут
        resp = await client.post(
            f"{settings.ROUTE_SERVICE_URL}/api/routes/{route_id}/cargo/{cargo_id}",
            headers=headers or {}
        )
        resp.raise_for_status()
        return route_id