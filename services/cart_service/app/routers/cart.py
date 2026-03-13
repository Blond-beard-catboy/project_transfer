from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List
from app.core.database import get_db
from app.schemas.cart import CartItemCreate, CartItemOut, CartItemWithCargo
from app.models.cart_item import CartItem
from app.dependencies import get_current_user
from app.clients.cargo_client import get_cargo
from app.clients.order_client import create_order

router = APIRouter(prefix="/cart", tags=["cart"])

@router.post("/items", response_model=CartItemOut)
async def add_to_cart(
    request: Request,  # добавьте этот параметр
    item: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    print("=== Incoming headers from Gateway ===")
    for key, value in request.headers.items():
        if key.lower().startswith("x-user"):  # покажем только наши заголовки
            print(f"{key}: {value}")
    print("=====================================")
    """Добавить груз в корзину текущего пользователя."""
    # Проверяем, есть ли уже такой груз в корзине
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user["id"],
            CartItem.cargo_id == item.cargo_id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Item already in cart")

    # Проверяем, существует ли груз в Cargo Service (опционально)
    try:
        await get_cargo(
            item.cargo_id,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="Cargo does not exist or unavailable")

    db_item = CartItem(user_id=current_user["id"], cargo_id=item.cargo_id)
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@router.get("/items", response_model=List[CartItemWithCargo])
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Получить все грузы в корзине текущего пользователя с дополнительной информацией."""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user["id"])
    )
    items = result.scalars().all()

    # Обогащаем данными из Cargo Service
    enriched_items = []
    for item in items:
        try:
            cargo = await get_cargo(
                item.cargo_id,
                headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
            )
            enriched = CartItemWithCargo(
                **item.__dict__,
                cargo_title=cargo.get("title"),
                cargo_weight=cargo.get("weight"),
                pickup_location=cargo.get("pickup_location"),
                delivery_location=cargo.get("delivery_location")
            )
            enriched_items.append(enriched)
        except Exception:
            # Если груз не найден, можно вернуть без доп.информации или пропустить
            enriched_items.append(CartItemWithCargo(**item.__dict__))
    return enriched_items

@router.delete("/items/{cargo_id}")
async def remove_from_cart(
    cargo_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Удалить груз из корзины."""
    result = await db.execute(
        delete(CartItem).where(
            CartItem.user_id == current_user["id"],
            CartItem.cargo_id == cargo_id
        )
    )
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    await db.commit()
    return {"message": "Item removed from cart"}

@router.post("/checkout")
async def checkout(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Оформить заказ на все грузы в корзине. Для каждого груза создаётся отдельный заказ."""
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == current_user["id"])
    )
    items = result.scalars().all()
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    orders = []
    errors = []
    for item in items:
        try:
            order = await create_order(
                cargo_id=item.cargo_id,
                customer_id=current_user["id"],
                headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
            )
            orders.append(order)
        except Exception as e:
            errors.append({"cargo_id": item.cargo_id, "error": str(e)})

    if errors:
        # Частичный успех – можно вернуть информацию об ошибках
        return {"message": "Some orders failed", "successful": orders, "errors": errors}

    # Если все успешно, очищаем корзину
    await db.execute(delete(CartItem).where(CartItem.user_id == current_user["id"]))
    await db.commit()
    return {"message": "Checkout successful", "orders": orders}