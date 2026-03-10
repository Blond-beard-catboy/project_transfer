import httpx
from app.core.config import get_settings

settings = get_settings()

async def create_payment(order_id: int, amount: float, due_date: str = None, headers: dict = None):
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{settings.PAYMENT_SERVICE_URL}/api/payments/",
            json={
                "order_id": order_id,
                "amount": amount,
                "due_date": due_date
            },
            headers=headers or {}
        )
        resp.raise_for_status()
        return resp.json()