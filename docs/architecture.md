# Архитектура системы

## Общая схема

```mermaid
flowchart TB
    subgraph Clients
        Client[Web / Mobile Frontend]
    end

    subgraph Gateway
        APIGW[API Gateway<br/>- JWT проверка<br/>- Correlation ID<br/>- Прокси]
    end

    subgraph Services
        UserS[User Service]
        CargoS[Cargo Service]
        RouteS[Route Service]
        OrderS[Order Service]
        NotifS[Notification Service]
        PaymentS[Payment Service]
        ParserS[Parser Service]
        CartS[Cart Service]
        AnalyticsS[Analytics Service]
    end

    subgraph Databases
        UserDB[(User DB)]
        CargoDB[(Cargo DB)]
        RouteDB[(Route DB)]
        OrderDB[(Order DB)]
        NotifDB[(Notification DB)]
        PaymentDB[(Payment DB)]
        ParserDB[(Parser DB)]
        CartDB[(Cart DB)]
        AnalyticsDB[(Analytics DB)]
    end

    subgraph ExternalMocks
        MapsMock[Карты (заглушка)]
        EmailMock[Email/SMS (лог)]
        ExchangeMock[Внешние биржи (заглушка)]
    end

    Client --> APIGW
    APIGW --> UserS & CargoS & RouteS & OrderS & NotifS & PaymentS & ParserS & CartS & AnalyticsS

    UserS --> UserDB
    CargoS --> CargoDB
    RouteS --> RouteDB
    OrderS --> OrderDB
    NotifS --> NotifDB
    PaymentS --> PaymentDB
    ParserS --> ParserDB
    CartS --> CartDB
    AnalyticsS --> AnalyticsDB

    OrderS -.-> CargoS
    OrderS -.-> RouteS
    OrderS -.-> NotifS
    OrderS -.-> PaymentS
    RouteS -.-> CargoS
    CartS -.-> CargoS
    CartS -.-> OrderS
    ParserS -.-> CargoS
    AnalyticsS -.-> OrderS

    RouteS -.-> MapsMock
    NotifS -.-> EmailMock
    CargoS -.-> ExchangeMock
```

## Описание взаимодействий

- **Клиенты** (Web/Mobile) отправляют запросы к **API Gateway**.
- **Gateway** проверяет JWT-токен (кроме публичных путей) и проксирует запросы к соответствующему микросервису в зависимости от префикса пути.
- Gateway добавляет заголовки `X-User-ID`, `X-User-Role` (из токена) и `X-Correlation-ID` для downstream сервисов.
- Каждый сервис имеет собственную базу данных PostgreSQL (отдельные базы в одном инстансе).

### Основные интеграции
- **Order Service** при создании заказа:
  - Проверяет существование груза через Cargo Service.
  - Создаёт маршрут через Route Service (вызов `POST /routes` и добавление груза).
  - Сохраняет заказ с полученным `route_id`.
  - При подтверждении заказа генерирует PDF-договор, отправляет уведомление через Notification Service и создаёт платёж через Payment Service.
- **Route Service** при добавлении груза в маршрут запрашивает данные груза у Cargo Service и создаёт точки погрузки/разгрузки.
- **Cart Service** управляет корзиной пользователя, проверяет грузы через Cargo Service и при оформлении заказа вызывает Order Service для каждого груза.
- **Parser Service** эмулирует парсинг внешних источников, сохраняет данные в свою БД и позволяет импортировать их в Cargo Service.
- **Analytics Service** периодически (или по запросу) получает данные из Order Service, агрегирует их и сохраняет в свои таблицы для быстрых отчётов.
- Все внешние зависимости (карты, отправка email, биржи) заменены заглушками внутри сервисов.

## Аутентификация и безопасность
- Пользователи аутентифицируются в User Service, получая JWT-токен.
- API Gateway проверяет токен и извлекает из него `user_id` и `role`.
- В downstream сервисы Gateway передаёт эти данные через заголовки `X-User-ID` и `X-User-Role`.
- Для внутренних вызовов между сервисами (например, Analytics → Order) используется служебный заголовок `X-Internal-Request: true`, позволяющий обойти стандартную аутентификацию.

## Масштабируемость и отказоустойчивость
- Каждый сервис изолирован и может быть масштабирован независимо.
- Базы данных разделены, что предотвращает конфликты при масштабировании.
- В учебном проекте синхронное взаимодействие, но при необходимости можно заменить на асинхронные очереди (например, для уведомлений).

## Заглушки внешних систем
- **Карты**: в Route Service реализована простая функция расчёта расстояния (гаверсинус или константа).
- **Email/SMS**: Notification Service пишет уведомления в лог вместо реальной отправки.
- **Биржи грузов**: Cargo Service имеет эндпоинт для импорта тестовых данных из JSON.
```