from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from app.core.config import get_settings

settings = get_settings()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Публичные пути (не требуют токена)
        open_paths = ["/docs", "/openapi.json", "/redoc", "/api/users/login", "/api/users/register"]
        if request.url.path in open_paths:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
            print(f"AuthMiddleware: user_id={request.state.user_id}, user_role={request.state.user_role}")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        response = await call_next(request)
        return response