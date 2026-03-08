import logging
logger = logging.getLogger(__name__)

async def send_notification(user_id: int, subject: str, body: str, notif_type: str = "email"):
    logger.info(f"📨 Уведомление для user {user_id}: {subject} - {body}")
    return True