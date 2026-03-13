# Файл: 01_architecture_and_diagram.md
## 1. Общая архитектура микросервисной системы

Система состоит из шести микросервисов, взаимодействующих через синхронные HTTP-запросы. Каждый сервис имеет собственную базу данных. API Gateway выступает единой точкой входа для клиентов.

### Диаграмма взаимодействия (Mermaid-код)

```mermaid
flowchart TB
    subgraph Clients
        A[Web / Mobile Frontend]
    end

    subgraph Gateway
        B[API Gateway]
    end

    subgraph Services
        C[User Service]
        D[Cargo Service]
        E[Order Service]
        F[Route Service]
        G[Notification Service]
    end

    subgraph Databases
        H[(User DB)]
        I[(Cargo DB)]
        J[(Order DB)]
        K[(Route DB)]
        L[(Notification DB)]
    end

    subgraph ExternalMocks
        M[Карты (заглушка)]
        N[Email/SMS (лог)]
        O[Внешние биржи (тестовые данные)]
    end

    A --> B
    B --> C & D & E & F & G

    C --> H
    D --> I
    E --> J
    F --> K
    G --> L

    E -.-> D
    E -.-> F
    F -.-> D
    E -.-> G

    F -.-> M
    G -.-> N
    D -.-> O

Описание диаграммы словами:
Клиенты (Web/Mobile) отправляют запросы к API Gateway.

Gateway проверяет JWT-токен и перенаправляет запросы к нужному микросервису в зависимости от пути:

/api/users/* → User Service

/api/cargo/* → Cargo Service

/api/orders/* → Order Service

/api/routes/* → Route Service

/api/notifications/* → Notification Service

Каждый сервис работает со своей базой данных (PostgreSQL).

Order Service при создании заказа обращается к Cargo Service (проверка груза) и к Route Service (создание маршрута). При изменении статуса заказа отправляет уведомление через Notification Service.

Route Service при добавлении груза в маршрут запрашивает данные груза у Cargo Service.

Внешние зависимости (карты, email, биржи) заменены заглушками внутри сервисов:

Route Service использует заглушку для расчёта расстояний.

Notification Service логирует отправку вместо реальной отправки.

Cargo Service может импортировать тестовые данные из JSON вместо реальных бирж.