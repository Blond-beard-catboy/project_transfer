from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIDMiddleware
from app.core.database import engine, Base
from app.routers import router  # нужно будет создать
from app.routers import cargo

setup_logging()
settings = get_settings()

app = FastAPI(title=settings.SERVICE_NAME)
app.include_router(cargo.router, prefix="/api")
app.add_middleware(CorrelationIDMiddleware)

@app.on_event("startup")
async def startup():
    # Создание таблиц (упрощённо, без миграций)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()

app.include_router(router, prefix="/api")