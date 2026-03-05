from fastapi import APIRouter
from .cargo import router as cargo_router

router = APIRouter()
router.include_router(cargo_router)