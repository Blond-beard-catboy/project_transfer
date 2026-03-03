from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
import jwt
from app.core.config import get_settings

settings = get_settings()

# Заглушка для get_current_user (будет переопределена в User Service)
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    # В других сервисах будет реальная проверка через заголовки от Gateway
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"id": int(user_id), "role": request.headers.get("X-User-Role")}