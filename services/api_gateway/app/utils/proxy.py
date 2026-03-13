import httpx
from fastapi import Request, Response
from typing import Dict

async def proxy_request(request: Request, base_url: str):
    client = httpx.AsyncClient(base_url=base_url)
    url = httpx.URL(path=request.url.path, query=request.url.query.encode())
    headers = dict(request.headers)

    # Добавляем служебные заголовки из состояния запроса
    if hasattr(request.state, "user_id"):
        headers["X-User-ID"] = str(request.state.user_id)
        headers["X-User-Role"] = request.state.user_role
    if hasattr(request.state, "correlation_id"):
        headers["X-Correlation-ID"] = request.state.correlation_id

    # Удаляем заголовки, которые могут мешать
    headers.pop("host", None)
    headers.pop("authorization", None)  # можно оставить, но обычно не нужно

    print(f"Proxy request to {base_url}{request.url.path}")
    print(f"Outgoing headers: { {k: v for k, v in headers.items() \
                                 if k.lower().startswith('x-')} }")

    resp = await client.request(
        method=request.method,
        url=str(url),
        headers=headers,
        content=await request.body()
    )
    return Response(content=resp.content, status_code=resp.status_code,\
                    headers=dict(resp.headers))