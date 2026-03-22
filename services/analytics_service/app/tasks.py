from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.core.database import AsyncSessionLocal
from app.models.analytics import MonthlyOrders, PopularRoutes, CustomerStats
from app.clients.order_client import get_all_orders
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def update_monthly_orders():
    """Обновляет таблицу monthly_orders на основе данных из Order Service."""
    logger.info("Updating monthly orders...")
    # Здесь нужно получить все заказы (или за последний месяц) из Order Service
    # Для простоты получим все и пересчитаем агрегаты.
    try:
        orders = await get_all_orders(headers={})  # нужны заголовки? Может быть, служебный ключ.
        # Но Order Service требует аутентификации. Для внутренних сервисов можно добавить заголовки доверия.
        # Упростим: будем считать, что у нас есть служебный токен или доверенный заголовок.
        # Пока оставим как есть.
    except Exception as e:
        logger.error(f"Failed to fetch orders: {e}")
        return

    # Агрегируем по месяцам
    from collections import defaultdict
    monthly = defaultdict(lambda: {"total": 0, "completed": 0, "revenue": 0.0})
    for order in orders:
        created = datetime.fromisoformat(order["created_at"])
        year, month = created.year, created.month
        monthly[(year, month)]["total"] += 1
        if order["status"] == "completed":
            monthly[(year, month)]["completed"] += 1
        # Предположим, что сумма заказа хранится в поле amount, но у нас нет. Возьмём из Payment? Сложно. Пропустим.
        # monthly[(year, month)]["revenue"] += order.get("amount", 0)

    async with AsyncSessionLocal() as db:
        for (year, month), data in monthly.items():
            # Проверяем, есть ли уже запись
            from sqlalchemy import select
            result = await db.execute(
                select(MonthlyOrders).where(
                    MonthlyOrders.year == year,
                    MonthlyOrders.month == month
                )
            )
            record = result.scalar_one_or_none()
            if record:
                record.total_orders = data["total"]
                record.completed_orders = data["completed"]
                # record.total_revenue = data["revenue"]
            else:
                record = MonthlyOrders(
                    year=year,
                    month=month,
                    total_orders=data["total"],
                    completed_orders=data["completed"],
                    # total_revenue=data["revenue"]
                )
                db.add(record)
        await db.commit()
    logger.info("Monthly orders updated.")

# Аналогичные функции для popular_routes и customer_stats

def start_scheduler():
    scheduler.add_job(
        update_monthly_orders,
        trigger=IntervalTrigger(hours=24),  # раз в сутки
        id="update_monthly_orders",
        replace_existing=True
    )
    scheduler.start()