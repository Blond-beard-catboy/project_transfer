import httpx
from app.core.config import get_settings

settings = get_settings()

async def get_all_orders(headers: dict = None):
    # Добавляем служебный заголовок для внутренних вызовов
    internal_headers = {"X-Internal-Request": "true"}
    if headers:
        internal_headers.update(headers)
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.ORDER_SERVICE_URL}/api/orders/",
            headers=internal_headers
        )
        resp.raise_for_status()
        return resp.json()