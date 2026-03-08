from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import os

def generate_contract(order_id: int, cargo_data: dict, customer_name: str = "Заказчик") -> str:
    """Генерирует PDF-договор и возвращает путь к файлу."""
    # Создаём папку для договоров, если её нет
    os.makedirs("contracts", exist_ok=True)
    filename = f"contracts/order_{order_id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    c.drawString(100, 800, f"ДОГОВОР № {order_id}")
    c.drawString(100, 780, f"Груз: {cargo_data.get('title', 'Н/Д')}")
    c.drawString(100, 760, f"Вес: {cargo_data.get('weight', 0)} кг")
    c.drawString(100, 740, f"Откуда: {cargo_data.get('pickup_location', '')}")
    c.drawString(100, 720, f"Куда: {cargo_data.get('delivery_location', '')}")
    c.drawString(100, 700, f"Заказчик: {customer_name}")
    c.save()
    return filename