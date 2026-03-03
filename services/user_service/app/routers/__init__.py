from fastapi import APIRouter
from .auth import router as auth_router

# Собираем все роутеры в один
router = APIRouter()
router.include_router(auth_router)