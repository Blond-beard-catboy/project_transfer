from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
# from app.models.user import User  # здесь нет модели User, только заголовки

async def get_current_user(request: Request):
    """Получение информации о пользователе из заголовков, добавленных Gateway."""
    user_id = request.headers.get("X-User-ID")
    user_role = request.headers.get("X-User-Role")
    if not user_id or not user_role:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": int(user_id), "role": user_role}