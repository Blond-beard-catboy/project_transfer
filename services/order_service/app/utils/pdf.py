from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from datetime import datetime

def generate_contract(order_id: int, cargo_data: dict, customer_name: str = "Заказчик", driver_name: str = "Не назначен") -> str:
    """Генерирует PDF-договор с улучшенным форматированием."""
    os.makedirs("contracts", exist_ok=True)
    filename = f"contracts/order_{order_id}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Заголовок
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, f"ДОГОВОР № {order_id}")

    # Дата
    c.setFont("Helvetica", 10)
    c.drawString(450, height - 50, f"Дата: {datetime.now().strftime('%d.%m.%Y')}")

    # Информация о сторонах
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 80, "Заказчик:")
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 95, customer_name)

    c.setFont("Helvetica-Bold", 12)
    c.drawString(300, height - 80, "Водитель:")
    c.setFont("Helvetica", 12)
    c.drawString(300, height - 95, driver_name)

    # Данные груза
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 130, "Данные груза:")

    data = [
        ["Наименование", cargo_data.get("title", "")],
        ["Описание", cargo_data.get("description", "")],
        ["Вес (кг)", str(cargo_data.get("weight", 0))],
        ["Пункт погрузки", cargo_data.get("pickup_location", "")],
        ["Пункт разгрузки", cargo_data.get("delivery_location", "")],
        ["Дата погрузки", cargo_data.get("pickup_date", "")[:10]],
        ["Дата разгрузки", cargo_data.get("delivery_date", "")[:10]],
    ]

    table = Table(data, colWidths=[100, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 280)

    # Стоимость (фиктивная)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 320, "Стоимость перевозки:")
    c.setFont("Helvetica", 12)
    cost = cargo_data.get("weight", 0) * 10  # например, 10 руб/кг
    c.drawString(50, height - 335, f"{cost} руб. (в т.ч. НДС)")

    # Подписи
    c.line(50, 150, 200, 150)
    c.drawString(50, 135, "Заказчик")
    c.line(300, 150, 450, 150)
    c.drawString(300, 135, "Водитель")

    c.save()
    return filename