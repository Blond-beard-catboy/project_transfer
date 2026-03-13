from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.schemas.cargo import CargoCreate, CargoUpdate, CargoOut
from app.models.cargo import Cargo, CargoStatus
from app.dependencies import get_current_user  # функция, которая получает user_id из заголовков (см. ниже)

router = APIRouter(prefix="/cargo", tags=["cargo"])

@router.post("/", response_model=CargoOut)
async def create_cargo(
    cargo: CargoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # ожидаем словарь с id и role
):
    """Создание нового груза. Владелец определяется из токена."""
    db_cargo = Cargo(
        **cargo.dict(),
        owner_id=current_user["id"]
    )
    db.add(db_cargo)
    await db.commit()
    await db.refresh(db_cargo)
    return db_cargo

@router.get("/", response_model=List[CargoOut])
async def list_cargos(
    status: Optional[CargoStatus] = Query(None),
    owner_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # можно ограничить доступ
):
    """Список грузов с фильтрацией."""
    query = select(Cargo)
    if status:
        query = query.where(Cargo.status == status)
    if owner_id:
        query = query.where(Cargo.owner_id == owner_id)
    # Если пользователь не админ, показываем только свои грузы
    if current_user["role"] != "admin":
        query = query.where(Cargo.owner_id == current_user["id"])
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    cargos = result.scalars().all()
    return cargos

@router.get("/{cargo_id}", response_model=CargoOut)
async def get_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Детальная информация о грузе."""
    cargo = await db.get(Cargo, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    # Проверка доступа (владелец или админ)
    if cargo.owner_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return cargo

@router.put("/{cargo_id}", response_model=CargoOut)
async def update_cargo(
    cargo_id: int,
    cargo_update: CargoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Обновление груза (только владелец или админ)."""
    cargo = await db.get(Cargo, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    if cargo.owner_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    for field, value in cargo_update.dict(exclude_unset=True).items():
        setattr(cargo, field, value)
    
    await db.commit()
    await db.refresh(cargo)
    return cargo

@router.delete("/{cargo_id}")
async def delete_cargo(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удаление груза (только владелец или админ)."""
    cargo = await db.get(Cargo, cargo_id)
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo not found")
    if cargo.owner_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await db.delete(cargo)
    await db.commit()
    return {"message": "Cargo deleted"}

# Заглушка импорта тестовых данных
@router.post("/import-test")
async def import_test_cargos(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Импорт тестовых грузов из JSON-файла (только для админа)."""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")
    
    # Читаем файл test_cargos.json (можно положить рядом)
    import json
    import os
    
    file_path = os.path.join(os.path.dirname(__file__), "../../test_cargos.json")
    try:
        with open(file_path, "r") as f:
            test_cargos = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Test file not found")
    
    count = 0
    for cargo_data in test_cargos:
        # Можно задавать owner_id = current_user["id"] или фиксированный
        cargo_data["owner_id"] = current_user["id"]
        db_cargo = Cargo(**cargo_data)
        db.add(db_cargo)
        count += 1
    await db.commit()
    return {"message": f"Imported {count} test cargos"}