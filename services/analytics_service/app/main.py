from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIDMiddleware
from app.core.database import engine, Base
from app.routers import analytics
from app.tasks import start_scheduler

from fastapi.middleware.cors import CORSMiddleware

setup_logging()
settings = get_settings()


app = FastAPI(title=settings.SERVICE_NAME)
app.include_router(analytics.router, prefix="/api")
app.add_middleware(CorrelationIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()  # запускаем планировщик

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()
