from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json
import os
from app.core.database import get_db
from app.schemas.parsed_cargo import ParsedCargoCreate, ParsedCargoOut
from app.models.parsed_cargo import ParsedCargo
from app.dependencies import get_current_user
from app.clients.cargo_client import import_cargo_to_cargo_service
from datetime import datetime

router = APIRouter(prefix="/parser", tags=["parser"])

@router.post("/run", response_model=dict)
async def run_parser(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Запуск парсинга: читает test_cargos.json и сохраняет/обновляет записи."""
    # Только админ может запускать парсер
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    file_path = os.path.join(os.path.dirname(__file__), "../../test_cargos.json")
    try:
        with open(file_path, "r") as f:
            cargos = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Test file not found")

    created = 0
    updated = 0
    for item in cargos:
        # 🔽 Преобразование строковых дат в объекты datetime
        if isinstance(item.get("pickup_date"), str):
            try:
                item["pickup_date"] = datetime.fromisoformat(item["pickup_date"].replace('Z', '+00:00'))
            except ValueError:
                # Если формат не подходит, можно использовать другой парсер
                pass

        if isinstance(item.get("delivery_date"), str):
            try:
                item["delivery_date"] = datetime.fromisoformat(item["delivery_date"].replace('Z', '+00:00'))
            except ValueError:
                pass

        # Проверяем, есть ли уже груз с таким external_id
        result = await db.execute(
            select(ParsedCargo).where(ParsedCargo.external_id == item["external_id"])
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Обновляем существующий
            for key, value in item.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            updated += 1
        else:
            # Создаём новый
            db_item = ParsedCargo(**item)
            db.add(db_item)
            created += 1
    await db.commit()
    return {"created": created, "updated": updated}

@router.get("/cargos", response_model=List[ParsedCargoOut])
async def list_parsed_cargos(
    skip: int = 0,
    limit: int = 100,
    source: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Список спарсенных грузов с фильтрацией по источнику."""
    query = select(ParsedCargo)
    if source:
        query = query.where(ParsedCargo.source == source)
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/cargos/{cargo_id}", response_model=ParsedCargoOut)
async def get_parsed_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cargo = await db.get(ParsedCargo, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    return cargo

@router.post("/cargos/{cargo_id}/import", response_model=dict)
async def import_parsed_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Импортировать спарсенный груз в Cargo Service."""
    cargo = await db.get(ParsedCargo, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")

    # Подготовка данных для Cargo Service
    cargo_data = {
        "title": cargo.title,
        "description": cargo.description or "",
        "weight": cargo.weight,
        "pickup_location": cargo.pickup_location,
        "delivery_location": cargo.delivery_location,
        "pickup_date": cargo.pickup_date.isoformat(),
        "delivery_date": cargo.delivery_date.isoformat()
    }

    try:
        result = await import_cargo_to_cargo_service(
            cargo_data,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cargo service unavailable: {str(e)}")

    return {"message": "Cargo imported", "cargo_id": result["id"]}