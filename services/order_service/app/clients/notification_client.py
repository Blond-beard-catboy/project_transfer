import httpx
from app.core.config import get_settings

settings = get_settings()

async def send_notification(user_id: int, subject: str, body: str, notif_type: str = "email", headers: dict = None):
    async with httpx.AsyncClient() as client:
        # Если заголовки не переданы, используем пустой словарь
        headers = headers or {}
        resp = await client.post(
            f"{settings.NOTIFICATION_SERVICE_URL}/api/notifications/",
            json={
                "user_id": user_id,
                "type": notif_type,
                "subject": subject,
                "body": body
            },
            headers=headers
        )
        resp.raise_for_status()
        return resp.json()