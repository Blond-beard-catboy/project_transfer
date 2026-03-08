import httpx
from fastapi import Request, Response
from typing import Dict

async def proxy_request(request: Request, base_url: str) -> Response:
    """Проксирует запрос к указанному base_url, сохраняя метод, тело и заголовки."""
    client = httpx.AsyncClient(base_url=base_url)
    url = httpx.URL(path=request.url.path, query=request.url.query.encode())
    headers = dict(request.headers)

    # Добавляем служебные заголовки из состояния запроса
    if hasattr(request.state, "user_id"):
        headers["X-User-ID"] = str(request.state.user_id)
        headers["X-User-Role"] = request.state.user_role
    if hasattr(request.state, "correlation_id"):
        headers["X-Correlation-ID"] = request.state.correlation_id

    # Удаляем заголовки, которые могут мешать (например, host)
    headers.pop("host", None)

    resp = await client.request(
        method=request.method,
        url=str(url),
        headers=headers,
        content=await request.body()
    )
    return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))