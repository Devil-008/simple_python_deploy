import os
from datetime import datetime, timedelta, timezone

import jwt
from flask import Flask, jsonify, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

SECRET_KEY = os.getenv("JWT_SECRET", "agent24-demo-secret")
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = int(os.getenv("TOKEN_EXPIRY_MINUTES", "30"))

# Intentionally simple in-memory user store for Agent 24 testing.
USERS = {
    "manas": {
        "id": 1,
        "username": "manas",
        "password": "password123",
        "name": "Manas Das",
        "email": "manas@example.com",
        "role": "developer",
    }
}


def authenticate_user(username, password):
    """Return a user when credentials are valid, otherwise None."""
    user = USERS.get(username)

    if user is None:
        return None

    if user["password"] != password:
        return None

    return user


def create_access_token(user_id):
    """Create a short-lived JWT for the authenticated user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token):
    """Decode and validate a JWT, returning its payload."""
    return jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])


def get_user_by_id(user_id):
    """Find a user by numeric ID."""
    for user in USERS.values():
        if user["id"] == user_id:
            return user
    return None


@app.post("/api/login")
def login():
    """Authenticate a user and return a JWT."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "success": False,
            "error": "username and password are required"
        }), 400

    user = authenticate_user(username, password)

    if user is None:
        return jsonify({
            "success": False,
            "error": "Invalid username or password"
        }), 401

    token = create_access_token(user["id"])

    return jsonify({
        "success": True,
        "message": "Login successful",
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": TOKEN_EXPIRY_MINUTES * 60,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
    }), 200


@app.get("/api/user")
def get_user():
    """Return the authenticated user's profile."""
    auth_header = request.headers.get("Authorization", "")

    if not auth_header:
        return jsonify({
            "success": False,
            "error": "Authorization header is required"
        }), 401

    parts = auth_header.split(" ", 1)

    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return jsonify({
            "success": False,
            "error": "Authorization header must use Bearer token"
        }), 401

    try:
        payload = decode_token(parts[1].strip())
    except jwt.ExpiredSignatureError:
        return jsonify({
            "success": False,
            "error": "Token has expired"
        }), 401
    except jwt.InvalidTokenError:
        return jsonify({
            "success": False,
            "error": "Invalid token"
        }), 401

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Invalid token subject"
        }), 401

    user = get_user_by_id(user_id)

    if user is None:
        return jsonify({
            "success": False,
            "error": "User not found"
        }), 404

    return jsonify({
        "success": True,
        "data": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        }
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)
