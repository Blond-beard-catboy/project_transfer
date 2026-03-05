import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Формула гаверсинуса для расстояния в км."""
    R = 6371  # радиус Земли в км
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_distance(city1: str, city2: str) -> float:
    """
    Заглушка: возвращает фиксированное расстояние для пары городов.
    В реальности здесь был бы вызов API карт.
    """
    # Примитивный справочник координат городов
    coords = {
        "Москва": (55.7558, 37.6176),
        "Санкт-Петербург": (59.9343, 30.3351),
        "Краснодар": (45.0355, 38.9753),
        "Новосибирск": (55.0084, 82.9357)
    }
    if city1 in coords and city2 in coords:
        lat1, lon1 = coords[city1]
        lat2, lon2 = coords[city2]
        return round(calculate_distance(lat1, lon1, lat2, lon2), 2)
    return 100.0  # значение по умолчанию