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
