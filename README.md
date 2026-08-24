# Agent 24 Flask Test Target

A deliberately small Flask application designed to test the **Agent 24 AI-Assisted TDD Test Intelligence Platform**.

The application exposes exactly two API routes:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/login` | Authenticate a user and issue a JWT |
| GET | `/api/user` | Return the authenticated user's data |

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

## 6. Run Unit/API Tests

```bash
pytest -q
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

The included Postman collection can be imported into Postman/Newman.

## 8. Suggested Agent 24 User Story

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

## 9. Deliberate Code Structure for Agent 24

The implementation contains explicit responsibilities that Stage 5 should be able to identify:

```text
login()
    -> authenticate_user()
    -> create_access_token()

get_user()
    -> decode_token()
    -> get_user_by_id()
```

This makes it suitable for validating Agent 24's **responsible function mapping**.

## 10. Important Security Note

This project intentionally uses an in-memory user and a development JWT secret. It is a test target for Agent 24, not a production authentication service.

Do not use the default credentials or secret in a real application.
