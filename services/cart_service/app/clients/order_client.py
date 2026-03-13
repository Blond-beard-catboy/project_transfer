import httpx
from app.core.config import get_settings

settings = get_settings()

async def create_order(cargo_id: int, customer_id: int, headers: dict = None):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.ORDER_SERVICE_URL}/api/orders/",
            json={"cargo_id": cargo_id, "customer_id": customer_id},
            headers=headers or {}
        )
        resp.raise_for_status()
        return resp.json()