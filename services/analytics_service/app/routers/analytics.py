from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.analytics import MonthlyOrdersOut, PopularRoutesOut, CustomerStatsOut
from app.models.analytics import MonthlyOrders, PopularRoutes, CustomerStats
from app.dependencies import get_current_user
from app.tasks import update_monthly_orders  # для ручного обновления

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/orders/monthly", response_model=List[MonthlyOrdersOut])
async def get_monthly_orders(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Только админ может смотреть аналитику? Или все, но свои? Оставим пока admin.
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    result = await db.execute(select(MonthlyOrders).order_by(MonthlyOrders.year, MonthlyOrders.month))
    return result.scalars().all()

@router.get("/routes/popular", response_model=List[PopularRoutesOut])
async def get_popular_routes(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    result = await db.execute(select(PopularRoutes).order_by(PopularRoutes.trips_count.desc()))
    return result.scalars().all()

@router.get("/customers/{customer_id}", response_model=CustomerStatsOut)
async def get_customer_stats(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Пользователь может смотреть только свою статистику, админ любую
    if current_user["role"] != "admin" and current_user["id"] != customer_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    result = await db.execute(
        select(CustomerStats).where(CustomerStats.customer_id == customer_id)
    )
    stats = result.scalar_one_or_none()
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return stats

@router.post("/refresh/monthly-orders")
async def refresh_monthly_orders(
    current_user: dict = Depends(get_current_user)
):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    await update_monthly_orders()
    return {"message": "Monthly orders updated"}