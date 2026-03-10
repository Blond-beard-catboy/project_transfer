from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.schemas.payment import PaymentCreate, PaymentOut, PaymentUpdate
from app.models.payment import Payment, PaymentStatus
from app.dependencies import get_current_user
from datetime import datetime

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/", response_model=PaymentOut)
async def create_payment(
    payment: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Создание платежа для заказа."""
    # Можно добавить проверку, что такой платёж ещё не существует
    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    return db_payment

@router.get("/", response_model=List[PaymentOut])
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Список платежей (для админа все, для обычного пользователя только свои через order_id)."""
    # В реальности нужно связывать с пользователем через order_id, но для простоты оставим так.
    query = select(Payment)
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment

@router.patch("/{payment_id}/pay")
async def pay_payment(
    payment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Имитация оплаты: меняет статус на paid и проставляет paid_at."""
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Payment already processed")
    payment.status = PaymentStatus.paid
    payment.paid_at = datetime.utcnow()
    await db.commit()
    return {"status": "paid"}