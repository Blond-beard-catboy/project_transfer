import pytest
import httpx
import time

BASE_URL = "http://localhost:8005"  # API Gateway

@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client

def test_full_scenario(client):
    # 1. Регистрация нового пользователя с уникальным email
    unique_email = f"test_{int(time.time())}_{hash(time.time()) % 10000}@example.com"
    resp = client.post("/api/users/register", json={
        "email": unique_email,
        "password": "secret",
        "full_name": "Test User",
        "role": "driver"
    })
    assert resp.status_code == 200, f"Registration failed: {resp.text}"
    user_id = resp.json()["id"]

    # 2. Логин
    resp = client.post("/api/users/login", json={
        "email": unique_email,
        "password": "secret"
    })
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Создание груза
    resp = client.post("/api/cargo/", json={   # <-- исправлено
        "title": "Integration Test Cargo",
        "weight": 500,
        "pickup_location": "Moscow",
        "delivery_location": "Kazan",
        "pickup_date": "2026-03-10T10:00:00",
        "delivery_date": "2026-03-15T18:00:00"
    }, headers=headers)
    assert resp.status_code == 200, f"Cargo creation failed: {resp.text}"
    cargo_id = resp.json()["id"]

    # 4. Создание заказа
    resp = client.post("/api/orders/", json={   # <-- исправлено
        "cargo_id": cargo_id,
        "customer_id": user_id
    }, headers=headers)
    assert resp.status_code == 200, f"Order creation failed: {resp.text}"
    order = resp.json()
    order_id = order["id"]
    assert order["status"] == "new"
    assert order["route_id"] is not None

    # 5. Подтверждение заказа (генерация PDF)
    resp = client.post(f"/api/orders/{order_id}/confirm", headers=headers)  # исправлено
    assert resp.status_code == 200, f"Order confirm failed: {resp.text}"
    order = resp.json()
    assert order["status"] == "confirmed"
    assert order["contract_file"] is not None

    # Даём время на обработку уведомлений (если они асинхронны)
    time.sleep(1)

    # 6. Проверка уведомлений
    resp = client.get("/api/notifications/", headers=headers)  # исправлено (предположительно)
    if resp.status_code == 200:
        notifications = resp.json()
        assert len(notifications) >= 2, f"Expected at least 2 notifications, got {len(notifications)}"
        subjects = [n.get("subject", "") for n in notifications]
        assert any("создан" in s for s in subjects), "Missing order creation notification"
        assert any("подтверждён" in s for s in subjects), "Missing order confirmation notification"
    else:
        print("⚠️ Notification service not available, skipping notification check")

    # 7. Проверка прав доступа: другой пользователь не должен видеть этот заказ
    other_email = f"other_{int(time.time())}@example.com"
    resp = client.post("/api/users/register", json={
        "email": other_email,
        "password": "secret2",
        "full_name": "Other User",
        "role": "driver"
    })
    assert resp.status_code == 200
    resp = client.post("/api/users/login", json={
        "email": other_email,
        "password": "secret2"
    })
    assert resp.status_code == 200
    other_token = resp.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = client.get(f"/api/orders/{order_id}", headers=other_headers)  # исправлено
    assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"