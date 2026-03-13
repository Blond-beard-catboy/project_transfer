from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.notification import NotificationCreate, NotificationOut
from app.models.notification import Notification, NotificationStatus
from app.dependencies import get_current_user
import asyncio
import logging

router = APIRouter(prefix="/notifications", tags=["notifications"])
logger = logging.getLogger(__name__)

async def emulate_sending(notification_id: int, db: AsyncSession):
    """Эмуляция отправки уведомления с задержкой."""
    await asyncio.sleep(2)  # имитация задержки отправки
    # Здесь можно было бы реально отправить email/SMS
    logger.info(f"📨 Уведомление {notification_id} отправлено")
    # Обновим статус в БД (потребуется отдельная сессия, поэтому здесь не делаем,
    # лучше сделать через фоновую задачу с отдельным соединением. Упростим: будем менять статус сразу при создании.)
    # Для простоты оставим синхронную эмуляцию.

@router.post("/", response_model=NotificationOut)
async def create_notification(
    notification: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создать уведомление и эмулировать отправку."""
    # Сохраняем в БД
    db_notif = Notification(**notification.dict(), status=NotificationStatus.pending)
    db.add(db_notif)
    await db.commit()
    await db.refresh(db_notif)

    # Эмулируем отправку (сразу меняем статус и логируем)
    db_notif.status = NotificationStatus.sent
    await db.commit()
    logger.info(f"📨 Уведомление для user {notification.user_id}: {notification.subject} - {notification.body}")

    return db_notif

@router.get("/", response_model=List[NotificationOut])
async def list_notifications(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Список уведомлений (для админа все, для обычного пользователя свои)."""
    query = select(Notification)
    if current_user["role"] != "admin":
        query = query.where(Notification.user_id == current_user["id"])
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()