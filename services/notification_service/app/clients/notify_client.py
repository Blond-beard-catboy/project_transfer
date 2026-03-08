import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

async def send_notification(user_id: int, subject: str, body: str, notif_type: str = "email"):
    """Заглушка отправки уведомления."""
    logger.info(f"📨 Уведомление для user {user_id}: {subject} - {body}")
    # Здесь потом будет вызов реального Notification Service
    return True