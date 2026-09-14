# Agent 24 Flask Test Target

A deliberately small Flask application designed to test the **Agent 24 AI-Assisted TDD Test Intelligence Platform**.

The application exposes the following API routes:

| Method | Endpoint | Purpose | Auth Required |
|---|---|---|---|
| POST | `/api/login` | Authenticate a user and issue a JWT | No |
| GET | `/api/user` | Return the authenticated user's data | Yes (Bearer JWT) |
| POST | `/api/tickets` | Create a support ticket with business validation | No |
| GET | `/api/tickets` | List tickets (optional `?category=` and `?status=` filters) | No |
| GET | `/api/tickets/<id>` | Retrieve support ticket details by ID | No |
| PATCH | `/api/tickets/<id>/status` | Update ticket lifecycle status (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`) | No |

## 1. Prerequisites

- Python 3.11+ recommended
- pip

## 2. Setup

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

The API runs on:

```text
http://localhost:5001
```

## 3. Test Credentials

```text
username: manas
password: password123
```

## 4. API Examples

### Login

```bash
curl -X POST http://localhost:5001/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"manas","password":"password123"}'
```

Expected:

```json
{
  "success": true,
  "message": "Login successful",
  "access_token": "<JWT>",
  "token_type": "Bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "manas",
    "name": "Manas Das",
    "email": "manas@example.com",
    "role": "developer"
  }
}
```

### Get User

Replace `<JWT>` with the token returned by login.

```bash
curl http://localhost:5001/api/user \
  -H "Authorization: Bearer <JWT>"
```

Expected:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "manas",
    "name": "Manas Das",
    "email": "manas@example.com",
    "role": "developer"
  }
}
```

### Create Support Ticket

```bash
curl -X POST http://localhost:5001/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title":"Database connection pool exhausted","description":"Backend pool hits limit during peak traffic","category":"technical","priority":"high"}'
```

Expected:

```json
{
  "success": true,
  "message": "Ticket created successfully",
  "data": {
    "id": 102,
    "ticket_key": "TCK-102",
    "title": "Database connection pool exhausted",
    "description": "Backend pool hits limit during peak traffic",
    "category": "technical",
    "priority": "high",
    "status": "OPEN",
    "tags": [],
    "created_at": "2026-09-14T11:55:00Z"
  }
}
```

### Get Ticket by ID

```bash
curl http://localhost:5001/api/tickets/101
```

### List Tickets (with optional filters)

```bash
curl "http://localhost:5001/api/tickets?category=technical&status=OPEN"
```

### Update Ticket Status

```bash
curl -X PATCH http://localhost:5001/api/tickets/101/status \
  -H "Content-Type: application/json" \
  -d '{"status":"IN_PROGRESS"}'
```

## 5. Negative Scenarios

Agent 24 should be able to discover and/or generate tests for:

### Login

- Missing JSON body
- Non-JSON request
- Missing username
- Missing password
- Empty username
- Empty password
- Unknown username
- Incorrect password
- Correct credentials
- Response schema validation
- JWT presence
- JWT type
- Expiration value

### Get User

- Missing Authorization header
- Empty Authorization header
- Wrong authentication scheme
- Missing Bearer token
- Malformed JWT
- Invalid JWT signature
- Expired JWT
- Invalid JWT subject
- Valid JWT
- Correct user payload
- Correct response status
- Response schema validation

### Support Ticket Management

- Missing required fields (title, description, or category)
- Non-JSON request payload
- Invalid category (only `technical`, `billing`, `account`, `feature` allowed)
- Invalid priority (only `low`, `medium`, `high`, `urgent` allowed)
- Boundary title length: reject < 5 characters
- Boundary title length: reject > 100 characters
- Boundary title length: accept exactly 5 and 100 characters
- Retrieve non-existent ticket ID (HTTP 404)
- Update status with missing `status` field (HTTP 400)
- Update status with invalid status value (HTTP 400)
- Update status of non-existent ticket ID (HTTP 404)

## 6. Run Unit/API Tests

```bash
pytest -v
```

## 7. Agent 24 Integration

Use this repository as the target Git workspace for Agent 24.

Recommended configuration:

```text
Target framework: Flask / Python
API runner: Newman
Code analyzer: Mock initially, SonarQube later
ALM: Mock initially
Vector store: Mock initially
```

## 8. Suggested Agent 24 User Stories

### Story 1: Authenticate user and retrieve authenticated user profile (PYTHON-101)

**Title**
```text
Authenticate user and retrieve authenticated user profile
```

**Description**
```text
As an application user,
I want to authenticate using my username and password,
so that I can securely access my user profile.
```

**Acceptance Criteria**
```text
AC1: The system shall authenticate a user when a valid username and password are supplied.
AC2: The system shall return a JWT access token after successful authentication.
AC3: The system shall reject invalid credentials with HTTP 401.
AC4: The system shall reject requests missing required login fields with HTTP 400.
AC5: The system shall allow an authenticated user to retrieve their profile using a valid Bearer JWT.
AC6: The system shall reject requests to the user endpoint when the Authorization header is missing.
AC7: The system shall reject invalid or expired JWT tokens with HTTP 401.
AC8: The user endpoint shall return the authenticated user's id, username, name, email, and role.
```

---

### Story 2: Support Ticket Management and Lifecycle (PYTHON-102)

**Title**
```text
Support Ticket Management and Lifecycle
```

**Description**
```text
As an application user or support agent,
I want to submit support tickets with structured details, retrieve existing tickets by ID, filter ticket listings, and transition ticket resolution statuses,
so that issues can be systematically recorded, tracked, and resolved.
```

**Acceptance Criteria**
```text
AC-01: The system shall create a support ticket and return HTTP 201 Created with ticket_key, title, description, category, priority, status ("OPEN"), and created_at when a valid JSON payload is submitted to POST /api/tickets.
AC-02: The system shall reject ticket creation with HTTP 400 Bad Request if title, description, or category is omitted or empty.
AC-03: The system shall reject ticket creation with HTTP 400 Bad Request if category is not one of: technical, billing, account, feature.
AC-04: The system shall reject ticket creation with HTTP 400 Bad Request if priority is provided and is not one of: low, medium, high, urgent.
AC-05: The system shall enforce ticket title length between 5 and 100 characters inclusive, rejecting titles with length < 5 or > 100 with HTTP 400 Bad Request.
AC-06: The system shall reject non-JSON request bodies with HTTP 400 Bad Request.
AC-07: The system shall return HTTP 200 OK and the full ticket record when a client requests GET /api/tickets/<ticket_id> for an existing ticket.
AC-08: The system shall return HTTP 404 Not Found with error "Ticket not found" when a client requests GET /api/tickets/<ticket_id> for a non-existent ticket.
AC-09: The system shall return HTTP 200 OK and an array of tickets matching optional query filters (category, status) when requested via GET /api/tickets.
AC-10: The system shall allow updating a ticket's status via PATCH /api/tickets/<ticket_id>/status to one of OPEN, IN_PROGRESS, RESOLVED, CLOSED, returning HTTP 200 OK with the updated record, and rejecting invalid status transitions with HTTP 400.
```

## 9. Deliberate Code Structure for Agent 24

The implementation contains explicit responsibilities that Stage 5 should be able to identify:

```text
# Domain 1: Authentication & User Profile
login()
    -> authenticate_user()
    -> create_access_token()

get_user()
    -> decode_token()
    -> get_user_by_id()

# Domain 2: Support Ticket Management
create_ticket_handler()
    -> validate_ticket_payload()
    -> create_ticket_record()

list_tickets_handler()
    -> list_tickets_records()

get_ticket_handler()
    -> get_ticket_by_id()

update_ticket_status_handler()
    -> update_ticket_status_record()
```

This makes it suitable for validating Agent 24's **responsible function mapping**.

## 10. Important Security Note

This project intentionally uses an in-memory user and a development JWT secret. It is a test target for Agent 24, not a production authentication service.

Do not use the default credentials or secret in a real application.
