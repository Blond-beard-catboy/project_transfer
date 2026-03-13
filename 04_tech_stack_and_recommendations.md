# Файл: 04_tech_stack_and_recommendations.md
## 4. Технологический стек и дополнительные рекомендации

### 4.1. Технологии
- **Язык:** Python 3.10+
- **Веб-фреймворк:** FastAPI
- **Базы данных:** PostgreSQL (каждый сервис – отдельная база в одном инстансе)
- **Аутентификация:** JWT (PyJWT), passlib (bcrypt)
- **API Gateway:** кастомный на FastAPI + httpx
- **Контейнеризация:** Docker, docker-compose
- **Очереди (опционально):** Redis + RQ
- **Тестирование:** pytest, pytest-httpx (для моков)
- **Логирование:** structlog или python-json-logger, correlation ID

### 4.2. Структурированное логирование и корреляция
- В каждом сервисе добавить middleware, которое:
  - Извлекает `X-Correlation-ID` из заголовков или генерирует новый UUID.
  - Добавляет correlation ID в `request.state` и в логи (через фильтр или адаптер).
- Формат логов – JSON, включающий поля: timestamp, service, correlation_id, level, message, дополнительно (user_id, order_id и т.д.).
- Пример настройки логгера:
  ```python
  import logging
  from pythonjsonlogger import jsonlogger

  logger = logging.getLogger()
  logHandler = logging.StreamHandler()
  formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
  logHandler.setFormatter(formatter)
  logger.addHandler(logHandler)

### 4.3. Заглушки внешних систем
- **Карты:** в Route Service можно реализовать простую функцию, вычисляющую расстояние по формуле гаверсинуса, если у точек есть координаты. Для учебных целей можно хранить координаты основных городов в справочнике.
- **Email/SMS:** в Notification Service уведомления выводятся в лог (например, `print(f"EMAIL to user {user_id}: {subject} - {body}")`). При желании можно добавить имитацию задержки через `asyncio.sleep`.
- **Внешние биржи грузов:** в Cargo Service можно создать эндпоинт `POST /cargo/import-test`, который загружает тестовые грузы из JSON-файла и сохраняет их в БД.
- **ЭДО/подписание:** генерация PDF в Order Service считается подписанием; никакой реальной ЭЦП не требуется.

### 4.4. Межсервисное взаимодействие
- Для HTTP-запросов между сервисами использовать `httpx.AsyncClient` с таймаутами и повторными попытками (retry).
- Желательно вынести клиенты в отдельные модули (например, `clients/cargo_client.py`) с настройкой базового URL из переменных окружения.
- Пример клиента:
  ```python
  import httpx
  from app.config import CARGO_SERVICE_URL

  async def get_cargo(cargo_id: int):
      async with httpx.AsyncClient() as client:
          resp = await client.get(f"{CARGO_SERVICE_URL}/cargo/{cargo_id}")
          resp.raise_for_status()
          return resp.json()

### 4.5. Управление конфигурацией
- Использовать переменные окружения (через pydantic-settings). Для каждого сервиса свой `.env` или общий с префиксами.
- Пример: `USER_SERVICE_DATABASE_URL`, `CARGO_SERVICE_URL` и т.д.

### 4.6. Базы данных
- Каждый сервис использует свою базу данных (разные имена: `user_db`, `cargo_db` и т.д.) в одном экземпляре PostgreSQL.
- Для инициализации нескольких баз можно использовать скрипт `create-multiple-dbs.sh` (см. документацию PostgreSQL).
- Для миграций можно использовать Alembic (опционально, упрощённо – создавать таблицы при старте через `create_all`).

### 4.7. Тестирование
- Модульные тесты для каждого сервиса (изолированные, с мок-объектами).
- Интеграционные тесты, запускающие все сервисы в docker-compose и проверяющие сквозные сценарии.
- Для моков внешних сервисов использовать `pytest-httpx`.