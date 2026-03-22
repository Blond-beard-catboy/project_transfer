# Запуск проекта

## Предварительные требования

- **Docker** и **docker-compose** (для запуска PostgreSQL и, опционально, всех сервисов).
- **Python 3.10+** (для локального запуска микросервисов).
- **Git** (для клонирования репозитория).

## Запуск через docker-compose (рекомендуемый)

1. Клонируйте репозиторий:
   ```bash
   git clone <repository-url>
   cd microservices-project
   ```

2. Создайте файл `.env` в корне проекта (можно скопировать из `.env.example`):
   ```bash
   cp .env.example .env
   ```
   Отредактируйте переменные окружения (особенно `JWT_SECRET`, пароли баз данных).

3. Запустите все сервисы:
   ```bash
   docker-compose up --build
   ```

4. После запуска API Gateway будет доступен по адресу `http://localhost:8005`.  
   Swagger-документация каждого сервиса доступна по адресам:

   | Сервис | Swagger URL |
   |--------|-------------|
   | User Service | `http://localhost:8000/docs` |
   | Cargo Service | `http://localhost:8001/docs` |
   | Route Service | `http://localhost:8002/docs` |
   | Order Service | `http://localhost:8003/docs` |
   | Notification Service | `http://localhost:8004/docs` |
   | Payment Service | `http://localhost:8006/docs` |
   | Parser Service | `http://localhost:8007/docs` |
   | Cart Service | `http://localhost:8008/docs` |
   | Analytics Service | `http://localhost:8009/docs` |
   | API Gateway | `http://localhost:8005/docs` |

5. Для остановки всех контейнеров:
   ```bash
   docker-compose down
   ```

## Локальный запуск (без Docker)

Этот способ требует ручного запуска каждого сервиса в отдельном терминале. Подходит для разработки и отладки.

### 1. Запустите PostgreSQL

Если вы используете Docker, запустите только контейнер с PostgreSQL:
```bash
docker-compose up -d postgres
```

Если PostgreSQL установлен локально, убедитесь, что он запущен.

### 2. Создайте базы данных

Подключитесь к PostgreSQL и создайте базы для каждого сервиса:
```bash
docker exec -it postgres psql -U postgres
```
В интерактивной консоли выполните:
```sql
CREATE DATABASE user_db;
CREATE DATABASE cargo_db;
CREATE DATABASE route_db;
CREATE DATABASE order_db;
CREATE DATABASE notification_db;
CREATE DATABASE payment_db;
CREATE DATABASE parser_db;
CREATE DATABASE cart_db;
CREATE DATABASE analytics_db;
\q
```

### 3. Настройте переменные окружения

Для каждого сервиса создайте файл `.env` в его папке (или используйте общий `.env` с префиксами). Пример для `user_service/.env`:
```ini
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=user_db
JWT_SECRET=super-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=30
```

Для других сервисов аналогично, меняя `POSTGRES_DB` и добавляя URL других сервисов (например, `CARGO_SERVICE_URL=http://localhost:8001`).

### 4. Запустите каждый сервис

Откройте отдельный терминал для каждого сервиса и выполните:

```bash
cd services/user_service
uvicorn app.main:app --reload --port 8000
```

Повторите для остальных, меняя порт:
- Cargo Service: `8001`
- Route Service: `8002`
- Order Service: `8003`
- Notification Service: `8004`
- API Gateway: `8005`
- Payment Service: `8006`
- Parser Service: `8007`
- Cart Service: `8008`
- Analytics Service: `8009`

**Важно**: API Gateway должен быть запущен последним, после всех остальных сервисов, чтобы маршруты были доступны.

### 5. Проверка работоспособности

После запуска всех сервисов выполните простой запрос через Gateway:
```bash
curl http://localhost:8005/docs
```

Если открывается страница Swagger – Gateway работает. Для проверки User Service:
```bash
curl -X POST "http://localhost:8005/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"secret","full_name":"Test","role":"driver"}'
```

## Переменные окружения (общий список)

Основные переменные, используемые в сервисах:

| Переменная | Описание | Пример |
|------------|----------|--------|
| `POSTGRES_USER` | Пользователь PostgreSQL | `postgres` |
| `POSTGRES_PASSWORD` | Пароль | `postgres` |
| `POSTGRES_HOST` | Хост базы данных | `localhost` (или `postgres` в Docker) |
| `POSTGRES_PORT` | Порт | `5432` |
| `POSTGRES_DB` | Имя базы для конкретного сервиса | `user_db`, `cargo_db` и т.д. |
| `JWT_SECRET` | Секретный ключ для подписи JWT | `super-secret-key` |
| `JWT_ALGORITHM` | Алгоритм подписи | `HS256` |
| `JWT_EXPIRATION_MINUTES` | Время жизни токена (минуты) | `30` |
| `USER_SERVICE_URL` | Адрес User Service | `http://localhost:8000` |
| `CARGO_SERVICE_URL` | Адрес Cargo Service | `http://localhost:8001` |
| `ROUTE_SERVICE_URL` | Адрес Route Service | `http://localhost:8002` |
| `ORDER_SERVICE_URL` | Адрес Order Service | `http://localhost:8003` |
| `NOTIFICATION_SERVICE_URL` | Адрес Notification Service | `http://localhost:8004` |
| `PAYMENT_SERVICE_URL` | Адрес Payment Service | `http://localhost:8006` |
| `PARSER_SERVICE_URL` | Адрес Parser Service | `http://localhost:8007` |
| `CART_SERVICE_URL` | Адрес Cart Service | `http://localhost:8008` |
| `ANALYTICS_SERVICE_URL` | Адрес Analytics Service | `http://localhost:8009` |

**Примечание:** для сервисов, запущенных в Docker-сети, вместо `localhost` следует указывать имя контейнера (например, `postgres`, `user_service`).

## Проверка работоспособности (быстрая)

После запуска всех сервисов выполните интеграционный тест:
```bash
pytest tests/e2e/test_full_scenario.py -v
```

Если тест зелёный – система работает корректно. Для ручной проверки используйте примеры из [testing.md](testing.md).
