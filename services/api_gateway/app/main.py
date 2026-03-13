from fastapi import FastAPI, Request
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.middleware.auth import AuthMiddleware
from app.core.middleware import CorrelationIDMiddleware
from app.utils.proxy import proxy_request

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.SERVICE_NAME)

# Добавляем middleware (порядок важен: сначала correlation, потом auth)
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(AuthMiddleware)

# Маршруты проксирования
@app.api_route("/api/users/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def users_proxy(request: Request, path: str):
    return await proxy_request(request, settings.USER_SERVICE_URL)

@app.api_route("/api/cargo/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def cargo_proxy(request: Request, path: str):
    return await proxy_request(request, settings.CARGO_SERVICE_URL)

@app.api_route("/api/routes/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def routes_proxy(request: Request, path: str):
    return await proxy_request(request, settings.ROUTE_SERVICE_URL)

@app.api_route("/api/orders/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def orders_proxy(request: Request, path: str):
    return await proxy_request(request, settings.ORDER_SERVICE_URL)

@app.api_route("/api/notifications/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def notifications_proxy(request: Request, path: str):
    return await proxy_request(request, settings.NOTIFICATION_SERVICE_URL)

@app.api_route("/api/cart/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def cart_proxy(request: Request, path: str):
    return await proxy_request(request, "http://localhost:8008")

@app.api_route("/api/payments/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def payments_proxy(request: Request, path: str):
    return await proxy_request(request, "http://localhost:8006")