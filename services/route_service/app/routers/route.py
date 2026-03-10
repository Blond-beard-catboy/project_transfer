from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List
from app.core.database import get_db
from app.schemas.route import (
    RouteCreate, RouteOut, RouteUpdate,
    RoutePointCreate, RoutePointOut, RoutePointUpdate
)
from app.models.route import Route, RoutePoint, RoutePointStatus
from app.dependencies import get_current_user
from services.route_service.app.clients.cargo_client import get_cargo
from datetime import datetime

router = APIRouter(prefix="/routes", tags=["routes"])

# ---------- Маршруты ----------
@router.post("/", response_model=RouteOut)
async def create_route(
    route: RouteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_route = Route(**route.model_dump())
    db.add(db_route)
    await db.commit()
    
    # Перезагружаем маршрут с точками (даже если их нет, это безопасно)
    result = await db.execute(
        select(Route)
        .where(Route.id == db_route.id)
        .options(selectinload(Route.points))
    )
    return result.scalar_one()

@router.get("/{route_id}", response_model=RouteOut)
async def get_route(
    route_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(
        select(Route)
        .where(Route.id == route_id)
        .options(selectinload(Route.points))
    )
    route = result.scalar_one_or_none()
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return route

@router.patch("/{route_id}", response_model=RouteOut)
async def update_route(
    route_id: int,
    route_update: RouteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновить статус маршрута или order_id."""
    route = await db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    for field, value in route_update.dict(exclude_unset=True).items():
        setattr(route, field, value)
    await db.commit()
    await db.refresh(route)
    return route

# ---------- Точки маршрута ----------
@router.post("/{route_id}/points", response_model=RoutePointOut)
async def add_point(
    route_id: int,
    point: RoutePointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Добавить точку в маршрут."""
    # Проверить существование маршрута
    route = await db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    db_point = RoutePoint(route_id=route_id, **point.dict())
    db.add(db_point)
    await db.commit()
    await db.refresh(db_point)
    return db_point

@router.patch("/{route_id}/points/{point_id}", response_model=RoutePointOut)
async def update_point(
    route_id: int,
    point_id: int,
    point_update: RoutePointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Отметить точку выполненной (установить actual_time и статус)."""
    point = await db.get(RoutePoint, point_id)
    if not point or point.route_id != route_id:
        raise HTTPException(status_code=404, detail="Point not found")
    
    if point_update.actual_time:
        point.actual_time = point_update.actual_time
    if point_update.status:
        point.status = point_update.status
    
    await db.commit()
    await db.refresh(point)
    return point

# ---------- Добавление груза в маршрут ----------
@router.post("/{route_id}/cargo/{cargo_id}", response_model=RouteOut)
async def add_cargo_to_route(
    route_id: int,
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Добавить груз в маршрут.
    Запрашивает данные груза из Cargo Service и создаёт две точки: pickup и delivery.
    """
    # 1. Проверить существование маршрута
    route = await db.get(Route, route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    
    # 2. Получить данные груза из Cargo Service
    try:
        cargo = await get_cargo(
            cargo_id,
            headers={
                "X-User-ID": str(current_user["id"]),
                "X-User-Role": current_user["role"]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cargo service unavailable: {str(e)}")
    
    # 3. Создать точки погрузки и разгрузки
    pickup_point = RoutePoint(
        route_id=route_id,
        type="pickup",
        cargo_id=cargo_id,
        address=cargo["pickup_location"],
        planned_time=None  # можно задать из груза, но в схеме Cargo нет planned_time, оставим None
    )
    delivery_point = RoutePoint(
        route_id=route_id,
        type="delivery",
        cargo_id=cargo_id,
        address=cargo["delivery_location"],
        planned_time=None
    )
    db.add_all([pickup_point, delivery_point])
    await db.commit()
    
    # 4. Вернуть обновлённый маршрут с точками
    result = await db.execute(
        select(Route)
        .where(Route.id == route_id)
        .options(selectinload(Route.points))
    )
    updated_route = result.scalar_one()
    return updated_route