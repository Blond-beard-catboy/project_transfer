from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import logging

logger = logging.getLogger(__name__)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Получаем correlation ID из заголовка или генерируем новый
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id

        # Добавляем correlation ID в логи (через контекст)
        # Для structlog можно использовать bound logger, но для простоты передадим в response

        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response