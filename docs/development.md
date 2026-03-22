# Руководство для разработчиков

## Структура проекта

```
microservices-project/
├── docker-compose.yml
├── .env.example
├── services/
│   ├── template/                 # Шаблон для новых микросервисов
│   ├── user_service/
│   ├── cargo_service/
│   ├── route_service/
│   ├── order_service/
│   ├── notification_service/
│   ├── payment_service/
│   ├── parser_service/
│   ├── cart_service/
│   ├── analytics_service/
│   └── api_gateway/
├── tests/
│   └── e2e/
│       └── test_full_scenario.py
├── scripts/
│   └── create-multiple-dbs.sh
├── docs/                         # Документация
└── README.md
```

## Как добавить новый микросервис

1. Скопируйте папку `template` в новую папку с именем сервиса:
   ```bash
   cp -r services/template services/new_service
   ```

2. Переименуйте модули и настройте:
   - В `app/core/config.py` измените `SERVICE_NAME`.
   - В `app/main.py` обновите подключение роутеров.
   - В `.env` задайте имя базы данных, порт и другие переменные.

3. Создайте базу данных в PostgreSQL:
   ```bash
   docker exec -it postgres psql -U postgres -c "CREATE DATABASE new_service_db;"
   ```

4. Реализуйте модели, схемы, роутеры.
5. Добавьте клиенты для вызовов других сервисов (если нужно).
6. Обновите API Gateway, добавив прокси-маршрут:
   ```python
   @app.api_route("/api/new_service/{path:path}", ...)
   async def new_service_proxy(request: Request, path: str):
       return await proxy_request(request, "http://localhost:8010")
   ```

7. Добавьте сервис в `docker-compose.yml` (если используете).

## Кодстайл и рекомендации

### Общие принципы
- Используйте **асинхронные эндпоинты** (`async def`).
- Для работы с БД используйте **SQLAlchemy 2.0 с asyncpg**.
- Все модели наследуются от `app.core.database.Base`.
- Для валидации данных используйте **Pydantic v2**.

### Именование
- Модели SQLAlchemy: существительное в единственном числе (например, `User`, `Order`).
- Схемы Pydantic: суффиксы `Create`, `Update`, `Out` (например, `UserCreate`, `UserUpdate`, `UserOut`).
- Функции в роутерах: глагол в инфинитиве (например, `create_user`, `list_users`).
- Переменные окружения: `UPPER_CASE`.

### Логирование
- Настройте JSON-логирование с полем `correlation_id`.
- Добавьте middleware `CorrelationIDMiddleware` из шаблона.
- В логах передавайте `extra={"correlation_id": get_correlation_id()}`.

### Аутентификация и авторизация
- В сервисах, кроме Gateway, используйте зависимость `get_current_user` из `dependencies.py`, которая извлекает `X-User-ID` и `X-User-Role` из заголовков.
- Для внутренних вызовов между сервисами используйте служебный заголовок `X-Internal-Request: true`, чтобы обойти аутентификацию.

### Межсервисное взаимодействие
- Используйте `httpx.AsyncClient` для HTTP-вызовов.
- Клиенты выносите в отдельные модули `app/clients/`.
- Добавляйте таймауты и обработку ошибок.

## Тестирование

### Модульные тесты
- Пишите тесты для каждого сервиса в папке `tests`.
- Используйте `pytest` и `pytest-asyncio`.
- Для изоляции можно мокировать зависимости (например, `httpx` через `pytest-httpx`).

### Интеграционные тесты
- Основной сценарий находится в `tests/e2e/test_full_scenario.py`.
- Тест запускает все сервисы (или использует моки) и проверяет цепочку операций.
- При добавлении нового сервиса расширяйте этот тест.

## Переменные окружения
Все настройки хранятся в `.env` (для каждого сервиса отдельный или общий). Обязательные переменные:
- `POSTGRES_*` – параметры подключения к БД.
- `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_EXPIRATION_MINUTES` – для аутентификации.
- `*_SERVICE_URL` – URL зависимых сервисов.

## Docker
Для локальной разработки удобно использовать Docker только для PostgreSQL:
```bash
docker-compose up -d postgres
```
Остальные сервисы запускаются локально с `uvicorn --reload`.

Для полного развёртывания добавьте все сервисы в `docker-compose.yml` и используйте `docker-compose up --build`.

## Добавление нового поля в существующую модель
1. Обновите SQLAlchemy модель.
2. Обновите Pydantic схему (если поле должно быть в ответе/запросе).
3. Примените миграцию (если используете Alembic) или удалите и пересоздайте таблицу (только для разработки).

## Полезные команды

```bash
# Запуск конкретного сервиса с авто-перезагрузкой
cd services/user_service
uvicorn app.main:app --reload --port 8000

# Запуск всех сервисов (вручную) – для удобства можно использовать скрипт
# или открыть несколько терминалов.

# Выполнение интеграционного теста
pytest tests/e2e/test_full_scenario.py -v

# Очистка Docker-контейнеров
docker-compose down -v
```

## Ресурсы
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic Documentation](https://docs.pydantic.dev/latest/)
- [httpx Documentation](https://www.python-httpx.org/)
```