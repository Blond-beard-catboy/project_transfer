
```markdown
# Файл: 02_microservices_description.md
## 2. Детальное описание каждого микросервиса

### 2.1. User Service
- **Назначение:** управление пользователями, аутентификация, выдача JWT.
- **Модель User:** id, email, hashed_password, role (driver/dispatcher/admin), full_name, created_at.
- **API:**
  - `POST /register` – регистрация нового пользователя.
  - `POST /login` – аутентификация, возвращает JWT.
  - `GET /me` – информация о текущем пользователе (требует токен).
- **Зависимости:** собственная БД, middleware проверки токена.

### 2.2. Cargo Service
- **Назначение:** CRUD для грузов, поиск, статусы.
- **Модель Cargo:** id, title, description, weight, pickup_location (строка), delivery_location (строка), pickup_date, delivery_date, owner_id (int), status (new, booked, in_transit, delivered), created_at.
- **API:**
  - `POST /cargo` – создание груза (владелец определяется из токена).
  - `GET /cargo` – список с фильтрацией (по статусу, датам, владельцу).
  - `GET /cargo/{id}` – детали.
  - `PUT /cargo/{id}` – обновление (только владелец или админ).
  - `DELETE /cargo/{id}` – удаление (только владелец или админ).
- **Заглушка внешней биржи:** эндпоинт для импорта тестовых грузов из локального JSON.

### 2.3. Route Service
- **Назначение:** создание маршрутов, добавление точек, управление выполнением.
- **Модели:**
  - **Route:** id, order_id (опционально), status (planned, in_progress, completed), created_at.
  - **RoutePoint:** id, route_id, type (pickup, delivery, service), cargo_id (опционально), address, planned_time, actual_time, status (pending, done).
- **API:**
  - `POST /routes` – создать пустой маршрут.
  - `POST /routes/{id}/points` – добавить точку.
  - `GET /routes/{id}` – получить маршрут с точками.
  - `PATCH /routes/{id}/points/{point_id}` – отметить точку выполненной.
  - `POST /routes/{id}/cargo/{cargo_id}` – добавить груз в маршрут (вызывает Cargo Service для получения данных груза и создаёт точки pickup/delivery).
- **Заглушка карт:** функция расчёта расстояния возвращает фиксированное значение (например, 100 км) или использует формулу гаверсинуса, если есть координаты.

### 2.4. Order Service
- **Назначение:** управление заказами (договорами), связь грузов, маршрутов и уведомлений.
- **Модель Order:** id, cargo_id, customer_id (владелец груза), driver_id (водитель), route_id, status (new, confirmed, in_progress, completed, cancelled), contract_file (путь к PDF), created_at.
- **API:**
  - `POST /orders` – создание заказа:
    1. Проверить cargo_id через Cargo Service (GET /cargo/{id}).
    2. Создать маршрут через Route Service (POST /routes и добавление точек по грузу).
    3. Сохранить заказ с route_id.
  - `GET /orders` – список.
  - `GET /orders/{id}` – детали.
  - `PATCH /orders/{id}/status` – изменить статус (при изменении на confirmed – генерировать PDF-договор; при любом изменении – отправить уведомление через Notification Service).
  - `POST /orders/{id}/confirm` – подтверждение заказа (имитация подписания): генерирует PDF-договор, сохраняет файл, обновляет статус.
- **Генерация PDF:** с помощью reportlab/fpdf; файл сохраняется в локальную папку (например, ./contracts).
- **Интеграции:** клиенты к Cargo, Route, Notification.

### 2.5. Notification Service
- **Назначение:** создание и эмуляция отправки уведомлений (email/SMS).
- **Модель Notification:** id, user_id, type (email, sms), subject, body, status (pending, sent, failed), created_at.
- **API:**
  - `POST /notify` – создать уведомление (сохраняет в БД, эмулирует отправку).
  - `GET /notifications` – история (для админа).
- **Эмуляция отправки:** сразу меняет статус на `sent` и пишет в лог (print или logger). При использовании очереди (опционально) ставит задачу в RQ, а воркер эмулирует отправку с задержкой.
- **Логирование:** каждое "отправленное" уведомление выводится в консоль с указанием получателя и текста.

### 2.6. API Gateway
- **Назначение:** единая точка входа, маршрутизация, проверка JWT, проброс correlation ID.
- **Функции:**
  - Проверка JWT в заголовке Authorization (кроме открытых путей, например /docs).
  - Добавление заголовков X-User-ID и X-User-Role для downstream сервисов.
  - Проксирование запросов к соответствующим микросервисам (на основе префикса пути).
  - Проброс/генерация correlation ID (заголовок X-Correlation-ID).
- **Реализация:** FastAPI с использованием httpx.AsyncClient для проксирования.