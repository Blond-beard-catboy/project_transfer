from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import logging

logger = logging.getLogger(__name__)

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Получить или сгенерировать correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Добавить в логи (через фильтр или в каждом логгере)
        # Временно сохраним в контексте (для structlog можно использовать bound logger)
        # Для простоты будем передавать через request.state
        
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response