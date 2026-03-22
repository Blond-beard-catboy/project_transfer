```markdown
# API Reference

Документация API доступна через встроенный Swagger UI каждого микросервиса. Ниже приведены ссылки и краткое описание основных эндпоинтов.

## Swagger UI

| Сервис | Адрес |
|--------|-------|
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

## Аутентификация

### Через API Gateway (рекомендовано)
- **Публичные эндпоинты** (регистрация, логин) не требуют токена.
- Для всех остальных эндпоинтов необходимо передавать JWT-токен в заголовке:
  ```
  Authorization: Bearer <token>
  ```
- Токен можно получить после успешного логина в User Service.

### Прямые вызовы микросервисов (минуя Gateway)
- При обращении напрямую к сервису (например, `http://localhost:8001/api/cargo`) требуется передача заголовков:
  ```
  X-User-ID: <user_id>
  X-User-Role: <role>
  ```
- Эти заголовки должны быть добавлены в запрос, так как сервисы не проверяют JWT самостоятельно.

## Основные эндпоинты

Ниже приведены примеры запросов для ключевых операций. Полный список доступен в Swagger.

### User Service (`/api/users`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/register` | Регистрация нового пользователя |
| POST | `/login` | Аутентификация, получение JWT-токена |
| GET | `/me` | Информация о текущем пользователе |
| PATCH | `/profile` | Обновление профиля (расширенные поля) |

**Пример регистрации:**
```bash
curl -X POST "http://localhost:8005/api/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secret",
    "full_name": "John Doe",
    "role": "driver"
  }'
```

**Пример логина:**
```bash
curl -X POST "http://localhost:8005/api/users/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret"}'
```

### Cargo Service (`/api/cargo`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/` | Создание груза |
| GET | `/` | Список грузов с фильтрацией |
| GET | `/{id}` | Детали груза |
| PUT | `/{id}` | Обновление груза |
| DELETE | `/{id}` | Удаление груза |
| POST | `/import-test` | Импорт тестовых грузов из JSON |

**Пример создания груза:**
```bash
curl -X POST "http://localhost:8005/api/cargo/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Стройматериалы",
    "weight": 5000,
    "pickup_location": "Москва",
    "delivery_location": "СПб",
    "pickup_date": "2026-03-15T08:00:00",
    "delivery_date": "2026-03-20T18:00:00"
  }'
```

### Route Service (`/api/routes`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/` | Создать пустой маршрут |
| GET | `/{id}` | Получить маршрут с точками |
| POST | `/{id}/cargo/{cargo_id}` | Добавить груз в маршрут (создаёт точки) |
| POST | `/{id}/points` | Добавить произвольную точку |
| PATCH | `/{id}/points/{point_id}` | Отметить точку выполненной |

**Пример добавления груза в маршрут:**
```bash
curl -X POST "http://localhost:8005/api/routes/1/cargo/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Order Service (`/api/orders`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/` | Создать заказ |
| GET | `/` | Список заказов |
| GET | `/{id}` | Детали заказа |
| PATCH | `/{id}/status` | Изменить статус |
| POST | `/{id}/confirm` | Подтвердить заказ (PDF, платёж) |
| POST | `/{id}/archive` | Архивировать заказ |
| POST | `/{id}/restore` | Восстановить из архива |

**Пример создания заказа:**
```bash
curl -X POST "http://localhost:8005/api/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cargo_id": 1, "customer_id": 1}'
```

**Пример подтверждения заказа:**
```bash
curl -X POST "http://localhost:8005/api/orders/1/confirm" \
  -H "Authorization: Bearer $TOKEN"
```

### Notification Service (`/api/notifications`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/` | Создать уведомление (эмуляция отправки) |
| GET | `/` | История уведомлений (для админа) |

**Пример создания уведомления:**
```bash
curl -X POST "http://localhost:8005/api/notifications/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"type":"email","subject":"Test","body":"Hello"}'
```

### Payment Service (`/api/payments`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/` | Создать платёж |
| GET | `/` | Список платежей |
| GET | `/{id}` | Детали платежа |
| PATCH | `/{id}/pay` | Имитация оплаты |

**Пример оплаты:**
```bash
curl -X PATCH "http://localhost:8005/api/payments/1/pay" \
  -H "Authorization: Bearer $TOKEN"
```

### Parser Service (`/api/parser`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/run` | Запустить парсинг (admin) |
| GET | `/cargos` | Список спарсенных грузов |
| POST | `/cargos/{id}/import` | Импортировать груз в Cargo Service |

**Пример импорта:**
```bash
curl -X POST "http://localhost:8005/api/parser/cargos/1/import" \
  -H "Authorization: Bearer $TOKEN"
```

### Cart Service (`/api/cart`)

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/items` | Добавить груз в корзину |
| GET | `/items` | Получить содержимое корзины |
| DELETE | `/items/{cargo_id}` | Удалить груз из корзины |
| POST | `/checkout` | Оформить заказ на все грузы в корзине |

**Пример добавления в корзину:**
```bash
curl -X POST "http://localhost:8005/api/cart/items" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cargo_id": 1}'
```

**Пример оформления заказа:**
```bash
curl -X POST "http://localhost:8005/api/cart/checkout" \
  -H "Authorization: Bearer $TOKEN"
```

### Analytics Service (`/api/analytics`)

| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/orders/monthly` | Количество заказов по месяцам (admin) |
| GET | `/routes/popular` | Популярные маршруты (admin) |
| GET | `/customers/{customer_id}` | Статистика клиента |
| POST | `/refresh/monthly-orders` | Принудительное обновление отчёта (admin) |

**Пример получения отчёта:**
```bash
curl -X GET "http://localhost:8005/api/analytics/orders/monthly" \
  -H "Authorization: Bearer $TOKEN"
```

---

Полную спецификацию API с подробным описанием всех полей и кодов ответов смотрите в Swagger каждого сервиса.
```