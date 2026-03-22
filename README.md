# Микросервисная система управления грузоперевозками

Данный проект представляет собой учебную реализацию микросервисной системы для управления грузоперевозками. Система состоит из девяти микросервисов, взаимодействующих через синхронные HTTP-запросы. API Gateway выступает единой точкой входа для клиентов.

## Содержание документации

- [Архитектура](docs/architecture.md) – диаграмма и описание взаимодействий.
- [Список микросервисов](docs/services.md) – порты и назначение.
- [Запуск проекта](docs/setup.md) – через docker-compose и локально.
- [Тестирование](docs/testing.md) – интеграционные тесты и ручные запросы.
- [API Reference](docs/api.md) – Swagger и основные эндпоинты.
- [Руководство для разработчиков](docs/development.md) – структура, добавление сервисов, кодстайл.

## Технологический стек

- **Python 3.12**, **FastAPI**, **SQLAlchemy 2.0** (async), **asyncpg**
- **Pydantic** для валидации
- **JWT** (PyJWT), **bcrypt**
- **httpx** для межсервисных вызовов
- **pytest**, **pytest-httpx** для тестирования
- **Docker**, **docker-compose**
- **reportlab** (генерация PDF), **apscheduler** (планировщик)

## Быстрый старт

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd microservices-project
   ```

2. Создайте файл `.env` из примера:
   ```bash
   cp .env.example .env
   ```
   Отредактируйте при необходимости (особенно `JWT_SECRET`).

3. Запустите все сервисы через docker-compose:
   ```bash
   docker-compose up --build
   ```

4. Откройте в браузере API Gateway: `http://localhost:8005/docs`

5. Выполните интеграционный тест (требуются запущенные сервисы):
   ```bash
   pytest tests/e2e/test_full_scenario.py -v
   ```

## Основные возможности

- Регистрация и аутентификация пользователей с ролями (driver, dispatcher, admin).
- Управление грузами (создание, фильтрация, импорт тестовых данных).
- Создание маршрутов и добавление грузов (автоматическое создание точек погрузки/разгрузки).
- Оформление заказов, генерация PDF-договоров, отправка уведомлений.
- Корзина грузов с возможностью массового оформления заказов.
- Платежи (создание и имитация оплаты).
- Парсер внешних данных о грузах.
- Аналитические отчёты (заказы по месяцам, популярные маршруты, статистика клиентов).
- Единый API Gateway с JWT-аутентификацией.

## Примеры использования

**Регистрация пользователя:**
```bash
curl -X POST "http://localhost:8005/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret","full_name":"User","role":"driver"}'
```

**Логин и получение токена:**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8005/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}' | jq -r '.access_token')
```

**Создание груза:**
```bash
curl -X POST "http://localhost:8005/api/cargo/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Груз","weight":100,"pickup_location":"A","delivery_location":"B","pickup_date":"2026-03-15T08:00:00","delivery_date":"2026-03-16T08:00:00"}'
```

**Добавление в корзину и оформление заказа:**
```bash
curl -X POST "http://localhost:8005/api/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cargo_id":1}'

curl -X POST "http://localhost:8005/api/cart/checkout" \
  -H "Authorization: Bearer $TOKEN"
```