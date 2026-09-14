import os
from datetime import datetime, timedelta, timezone

import jwt
# pyrefly: ignore [missing-import]
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


# -----------------------------------------------------------------------------
# Ticket Management Domain
# -----------------------------------------------------------------------------

VALID_CATEGORIES = {"technical", "billing", "account", "feature"}
VALID_PRIORITIES = {"low", "medium", "high", "urgent"}
VALID_STATUSES = {"OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"}

TICKETS = {
    101: {
        "id": 101,
        "ticket_key": "TCK-101",
        "title": "Database connection pool exhausted",
        "description": "Backend database pool hits limit during peak hours",
        "category": "technical",
        "priority": "high",
        "status": "OPEN",
        "tags": ["database", "infrastructure"],
        "created_by": 1,
        "created_at": "2026-09-08T10:00:00Z",
    }
}
_next_ticket_id = 102


def extract_auth_user():
    """Extract and authenticate user from Authorization Bearer header. Returns (user, error_response)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header:
        return None, (jsonify({"success": False, "error": "Authorization header is required"}), 401)

    parts = auth_header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return None, (jsonify({"success": False, "error": "Authorization header must use Bearer token"}), 401)

    try:
        payload = decode_token(parts[1].strip())
    except jwt.ExpiredSignatureError:
        return None, (jsonify({"success": False, "error": "Token has expired"}), 401)
    except jwt.InvalidTokenError:
        return None, (jsonify({"success": False, "error": "Invalid token"}), 401)

    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        return None, (jsonify({"success": False, "error": "Invalid token subject"}), 401)

    user = get_user_by_id(user_id)
    if user is None:
        return None, (jsonify({"success": False, "error": "User not found"}), 404)

    return user, None


def validate_ticket_payload(data):
    """Validate ticket input payload against business rules."""
    if not isinstance(data, dict):
        return "Request payload must be a JSON object"

    title = data.get("title")
    description = data.get("description")
    category = data.get("category")
    priority = data.get("priority", "medium")

    if not title or not description or not category:
        return "title, description, and category are required"

    if not isinstance(title, str) or len(title.strip()) < 5 or len(title.strip()) > 100:
        return "title must be between 5 and 100 characters"

    if not isinstance(category, str) or category.strip().lower() not in VALID_CATEGORIES:
        return f"Invalid category. Allowed values: {', '.join(sorted(VALID_CATEGORIES))}"

    if priority and (not isinstance(priority, str) or priority.strip().lower() not in VALID_PRIORITIES):
        return f"Invalid priority. Allowed values: {', '.join(sorted(VALID_PRIORITIES))}"

    return None


def create_ticket_record(data):
    """Create and persist a new support ticket record."""
    global _next_ticket_id
    ticket_id = _next_ticket_id
    _next_ticket_id += 1

    ticket_record = {
        "id": ticket_id,
        "ticket_key": f"TCK-{ticket_id}",
        "title": data["title"].strip(),
        "description": data["description"].strip(),
        "category": data["category"].strip().lower(),
        "priority": data.get("priority", "medium").strip().lower(),
        "status": "OPEN",
        "tags": data.get("tags") if isinstance(data.get("tags"), list) else [],
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    TICKETS[ticket_id] = ticket_record
    return ticket_record


def get_ticket_by_id(ticket_id):
    """Retrieve ticket dictionary by numeric ticket ID."""
    return TICKETS.get(ticket_id)


def list_tickets_records(category=None, status=None):
    """Retrieve all tickets, optionally filtered by category and/or status."""
    results = list(TICKETS.values())
    if category:
        category_clean = category.strip().lower()
        results = [t for t in results if t.get("category") == category_clean]
    if status:
        status_clean = status.strip().upper()
        results = [t for t in results if t.get("status") == status_clean]
    return results


def update_ticket_status_record(ticket_id, new_status):
    """Update status of a ticket. Returns (ticket, error_message)."""
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return None, "Ticket not found"

    if not new_status or not isinstance(new_status, str):
        return None, "status is required"

    normalized_status = new_status.strip().upper()
    if normalized_status not in VALID_STATUSES:
        return None, f"Invalid status. Allowed values: {', '.join(sorted(VALID_STATUSES))}"

    ticket["status"] = normalized_status
    ticket["updated_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return ticket, None


@app.post("/api/tickets")
def create_ticket_handler():
    """Create a support ticket (Public Endpoint - No Token Required)."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json(silent=True) or {}
    validation_err = validate_ticket_payload(data)
    if validation_err:
        return jsonify({
            "success": False,
            "error": validation_err
        }), 400

    new_ticket = create_ticket_record(data)

    return jsonify({
        "success": True,
        "message": "Ticket created successfully",
        "data": new_ticket
    }), 201


@app.get("/api/tickets")
@app.get("/api/tickets.")
def list_tickets_handler():
    """List all support tickets with optional filtering by category and status."""
    category = request.args.get("category")
    status = request.args.get("status")

    tickets = list_tickets_records(category=category, status=status)
    return jsonify({
        "success": True,
        "total": len(tickets),
        "data": tickets
    }), 200


@app.get("/api/tickets/<int:ticket_id>")
def get_ticket_handler(ticket_id):
    """Retrieve details for a specific support ticket (Public Endpoint - No Token Required)."""
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        return jsonify({
            "success": False,
            "error": "Ticket not found"
        }), 404

    return jsonify({
        "success": True,
        "data": ticket
    }), 200


@app.patch("/api/tickets/<int:ticket_id>/status")
def update_ticket_status_handler(ticket_id):
    """Update status of an existing ticket (OPEN, IN_PROGRESS, RESOLVED, CLOSED)."""
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Request body must be JSON"
        }), 400

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    if not new_status:
        return jsonify({
            "success": False,
            "error": "status field is required"
        }), 400

    ticket, err = update_ticket_status_record(ticket_id, new_status)
    if err == "Ticket not found":
        return jsonify({
            "success": False,
            "error": err
        }), 404
    if err:
        return jsonify({
            "success": False,
            "error": err
        }), 400

    return jsonify({
        "success": True,
        "message": f"Ticket status updated to {ticket['status']}",
        "data": ticket
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=True)

