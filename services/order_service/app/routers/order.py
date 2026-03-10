from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.order import OrderCreate, OrderOut, OrderUpdate
from app.models.order import Order, OrderStatus
from app.dependencies import get_current_user
from app.clients.cargo_client import get_cargo
from app.clients.route_client import create_route_for_cargo
from app.clients.notification_client import send_notification
from app.utils.pdf import generate_contract
from datetime import datetime
from app.clients.payment_client import create_payment

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderOut)
async def create_order(
    order: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание нового заказа."""
    # 1. Проверить существование груза через Cargo Service
    try:
        cargo = await get_cargo(
            order.cargo_id,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cargo service unavailable: {str(e)}")

    # 2. Создать маршрут через Route Service
    try:
        route_id = await create_route_for_cargo(
            order.cargo_id,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Route service unavailable: {str(e)}")

    # 3. Сохранить заказ в БД
    db_order = Order(
        cargo_id=order.cargo_id,
        customer_id=order.customer_id,
        driver_id=order.driver_id,
        route_id=route_id,
        status=OrderStatus.new
    )
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    # 4. Отправить уведомление о создании заказа (добавлены заголовки)
    await send_notification(
        user_id=order.customer_id,
        subject="Заказ создан",
        body=f"Ваш заказ №{db_order.id} успешно создан.",
        headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}  # <-- добавлено
    )

    return db_order

@router.get("/", response_model=List[OrderOut])
async def list_orders(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Список заказов (для админа все, для обычного пользователя только свои)."""
    query = select(Order)
    if current_user["role"] != "admin":
        query = query.where(Order.customer_id == current_user["id"])
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{order_id}", response_model=OrderOut)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Детальная информация о заказе."""
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    # Проверка прав: владелец или админ
    if order.customer_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return order

@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(
    order_id: int,
    status_update: OrderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Изменить статус заказа. При подтверждении генерируется PDF."""
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    old_status = order.status
    new_status = status_update.status
    if new_status:
        order.status = new_status
    
    if new_status == OrderStatus.cancelled and old_status != OrderStatus.cancelled:
    # Вызвать клиент для отмены платежа (если он был создан)
    # Например, отправить PATCH на payment service для отмены
        pass

    # Если статус меняется на confirmed, генерируем PDF
    if new_status == OrderStatus.confirmed and old_status != OrderStatus.confirmed:
        try:
            cargo = await get_cargo(
                order.cargo_id,
                headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
            )
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Cargo service unavailable: {str(e)}")

        filename = generate_contract(
    order.id,
    cargo,
    customer_name=f"User {order.customer_id}",
    driver_name=f"Driver {order.driver_id}" if order.driver_id else "Не назначен"
)
        order.contract_file = filename

    await db.commit()
    await db.refresh(order)

    # Отправляем уведомление об изменении статуса (добавлены заголовки)
    await send_notification(
        user_id=order.customer_id,
        subject="Статус заказа изменён",
        body=f"Статус заказа №{order.id} изменён на {order.status.value}.",
        headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}  # <-- добавлено
    )

    return order

@router.post("/{order_id}/confirm", response_model=OrderOut)
async def confirm_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Имитация подписания договора (меняет статус на confirmed и генерирует PDF)."""
    order = await db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.customer_id != current_user["id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if order.status != OrderStatus.new:
        raise HTTPException(status_code=400, detail="Only new orders can be confirmed")

    try:
        cargo = await get_cargo(
            order.cargo_id,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Cargo service unavailable: {str(e)}")

    filename = generate_contract(
    order.id,
    cargo,
    customer_name=f"User {order.customer_id}",
    driver_name=f"Driver {order.driver_id}" if order.driver_id else "Не назначен"
)
    order.contract_file = filename
    order.status = OrderStatus.confirmed

    await db.commit()
    await db.refresh(order)

        # Создаём платёж
    try:
        amount = cargo.get("weight", 0) * 10  # фиктивная стоимость
        await create_payment(
            order_id=order.id,
            amount=amount,
            headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}
        )
    except Exception as e:
        # Логируем ошибку, но не прерываем подтверждение (можно и прервать)
        print(f"Payment creation failed: {e}")

    # Уведомление о подтверждении (добавлены заголовки)
    await send_notification(
        user_id=order.customer_id,
        subject="Заказ подтверждён",
        body=f"Заказ №{order.id} подтверждён. Договор доступен.",
        headers={"X-User-ID": str(current_user["id"]), "X-User-Role": current_user["role"]}  # <-- добавлено
    )

    return order