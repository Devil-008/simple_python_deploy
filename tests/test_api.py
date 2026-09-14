import jwt
import pytest

from app import app, SECRET_KEY, JWT_ALGORITHM, create_access_token


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client


def test_login_success(client):
    response = client.post(
        "/api/login",
        json={"username": "manas", "password": "password123"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["token_type"] == "Bearer"
    assert body["access_token"]

    assert body["user"]["id"] == 1
    assert body["user"]["username"] == "manas"


def test_login_invalid_password(client):
    response = client.post(
        "/api/login",
        json={"username": "manas", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Invalid username or password"


def test_login_unknown_user(client):
    response = client.post(
        "/api/login",
        json={"username": "unknown", "password": "password123"},
    )

    assert response.status_code == 401


def test_login_missing_fields(client):
    response = client.post(
        "/api/login",
        json={"username": "manas"},
    )

    assert response.status_code == 400


def test_login_non_json(client):
    response = client.post(
        "/api/login",
        data="username=manas&password=password123",
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400


def test_get_user_without_authorization(client):
    response = client.get("/api/user")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authorization header is required"


def test_get_user_with_invalid_scheme(client):
    response = client.get(
        "/api/user",
        headers={"Authorization": "Basic abc123"},
    )

    assert response.status_code == 401


def test_get_user_with_invalid_token(client):
    response = client.get(
        "/api/user",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_get_user_success(client):
    token = create_access_token(1)

    response = client.get(
        "/api/user",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["id"] == 1
    assert body["data"]["username"] == "manas"
    assert body["data"]["role"] == "developer"


def test_get_user_rejects_expired_token(client):
    token = jwt.encode(
        {"sub": "1", "exp": 1},
        SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/api/user",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"] == "Token has expired"


def test_get_user_invalid_subject(client):
    token = jwt.encode(
        {"sub": "not-a-number"},
        SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )

    response = client.get(
        "/api/user",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


# -----------------------------------------------------------------------------
# Story 2: Support Ticket Management and Lifecycle (PYTHON-102)
# -----------------------------------------------------------------------------

def test_create_ticket_success(client):
    payload = {
        "title": "Payment gateway timeout on checkout",
        "description": "Requests to external gateway timeout after 30 seconds during checkout flow.",
        "category": "technical",
        "priority": "high",
        "tags": ["payment", "gateway"]
    }
    response = client.post("/api/tickets", json=payload)

    assert response.status_code == 201
    body = response.get_json()
    assert body["success"] is True
    assert body["message"] == "Ticket created successfully"

    ticket = body["data"]
    assert ticket["id"] > 0
    assert ticket["ticket_key"].startswith("TCK-")
    assert ticket["title"] == payload["title"]
    assert ticket["description"] == payload["description"]
    assert ticket["category"] == "technical"
    assert ticket["priority"] == "high"
    assert ticket["status"] == "OPEN"
    assert "created_at" in ticket


def test_create_ticket_missing_required_fields(client):
    # Missing category
    response = client.post(
        "/api/tickets",
        json={"title": "Valid Ticket Title", "description": "Some description"}
    )
    assert response.status_code == 400
    assert "required" in response.get_json()["error"]

    # Missing title
    response = client.post(
        "/api/tickets",
        json={"description": "Some description", "category": "technical"}
    )
    assert response.status_code == 400

    # Missing description
    response = client.post(
        "/api/tickets",
        json={"title": "Valid Ticket Title", "category": "technical"}
    )
    assert response.status_code == 400


def test_create_ticket_invalid_category(client):
    response = client.post(
        "/api/tickets",
        json={
            "title": "Valid Ticket Title",
            "description": "Some description",
            "category": "unsupported_cat"
        }
    )
    assert response.status_code == 400
    assert "Invalid category" in response.get_json()["error"]


def test_create_ticket_invalid_priority(client):
    response = client.post(
        "/api/tickets",
        json={
            "title": "Valid Ticket Title",
            "description": "Some description",
            "category": "technical",
            "priority": "super-urgent"
        }
    )
    assert response.status_code == 400
    assert "Invalid priority" in response.get_json()["error"]


def test_create_ticket_title_boundaries(client):
    # Too short (< 5 chars)
    resp_short = client.post(
        "/api/tickets",
        json={"title": "Bug", "description": "Valid description", "category": "technical"}
    )
    assert resp_short.status_code == 400

    # Too long (> 100 chars)
    resp_long = client.post(
        "/api/tickets",
        json={"title": "A" * 101, "description": "Valid description", "category": "technical"}
    )
    assert resp_long.status_code == 400

    # Exactly 5 chars -> should pass
    resp_exact_5 = client.post(
        "/api/tickets",
        json={"title": "12345", "description": "Valid description", "category": "technical"}
    )
    assert resp_exact_5.status_code == 201

    # Exactly 100 chars -> should pass
    resp_exact_100 = client.post(
        "/api/tickets",
        json={"title": "A" * 100, "description": "Valid description", "category": "technical"}
    )
    assert resp_exact_100.status_code == 201


def test_create_ticket_non_json(client):
    response = client.post(
        "/api/tickets",
        data="title=Test&description=Test",
        content_type="application/x-www-form-urlencoded"
    )
    assert response.status_code == 400
    assert response.get_json()["error"] == "Request body must be JSON"


def test_get_ticket_success(client):
    response = client.get("/api/tickets/101")
    assert response.status_code == 200

    body = response.get_json()
    assert body["success"] is True
    assert body["data"]["id"] == 101
    assert body["data"]["ticket_key"] == "TCK-101"
    assert body["data"]["title"] == "Database connection pool exhausted"


def test_get_ticket_not_found(client):
    response = client.get("/api/tickets/99999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Ticket not found"


def test_list_tickets_and_filtering(client):
    # Retrieve all tickets
    response = client.get("/api/tickets")
    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["total"] >= 1
    assert isinstance(body["data"], list)

    # Filter by category
    resp_filtered = client.get("/api/tickets?category=technical")
    assert resp_filtered.status_code == 200
    for t in resp_filtered.get_json()["data"]:
        assert t["category"] == "technical"

    # Filter by status
    resp_status = client.get("/api/tickets?status=OPEN")
    assert resp_status.status_code == 200
    for t in resp_status.get_json()["data"]:
        assert t["status"] == "OPEN"


def test_update_ticket_status_lifecycle(client):
    # 1. Create a fresh ticket
    create_resp = client.post(
        "/api/tickets",
        json={
            "title": "Lifecycle tracking ticket",
            "description": "Verify status progression",
            "category": "feature",
            "priority": "medium"
        }
    )
    ticket_id = create_resp.get_json()["data"]["id"]

    # 2. Transition to IN_PROGRESS
    res_ip = client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "IN_PROGRESS"})
    assert res_ip.status_code == 200
    assert res_ip.get_json()["data"]["status"] == "IN_PROGRESS"

    # 3. Transition to RESOLVED
    res_res = client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "RESOLVED"})
    assert res_res.status_code == 200
    assert res_res.get_json()["data"]["status"] == "RESOLVED"

    # 4. Transition to CLOSED
    res_close = client.patch(f"/api/tickets/{ticket_id}/status", json={"status": "CLOSED"})
    assert res_close.status_code == 200
    assert res_close.get_json()["data"]["status"] == "CLOSED"


def test_update_ticket_status_validations(client):
    # Non-existent ticket
    res_nf = client.patch("/api/tickets/99999/status", json={"status": "CLOSED"})
    assert res_nf.status_code == 404

    # Missing status field
    res_missing = client.patch("/api/tickets/101/status", json={})
    assert res_missing.status_code == 400

    # Invalid status value
    res_inv = client.patch("/api/tickets/101/status", json={"status": "CANCELLED_INVALID"})
    assert res_inv.status_code == 400
    assert "Invalid status" in res_inv.get_json()["error"]

