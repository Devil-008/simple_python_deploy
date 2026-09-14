# User Story: Support Ticket Management and Lifecycle

**Story Key**: `PYTHON-102`  
**Project**: `Auth-python` (`PYTHON`)  
**Sprint**: `Sprint 1`  
**Status**: `ready`  

---

## User Story Narrative

**As an** application user or support engineer,  
**I want to** submit support tickets with structured details, retrieve existing tickets by numeric ID, list all tickets with optional category/status filtering, and transition ticket resolution statuses,  
**So that** customer issues and technical requests can be systematically reported, tracked, and resolved without authentication roadblocks.

---

## Technical Overview & API Specifications

| Method | Endpoint | Description | Expected Status |
|---|---|---|---|
| `POST` | `/api/tickets` | Create a new support ticket with business validation | `201 Created` / `400 Bad Request` |
| `GET` | `/api/tickets/<ticket_id>` | Retrieve specific ticket record by numeric ID | `200 OK` / `404 Not Found` |
| `GET` | `/api/tickets` | List tickets with optional `?category=` and `?status=` filters | `200 OK` |
| `PATCH` | `/api/tickets/<ticket_id>/status` | Update ticket lifecycle status (`OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`) | `200 OK` / `400 Bad Request` / `404 Not Found` |

### Business Rules & Constraints:
- **Allowed Categories**: `technical`, `billing`, `account`, `feature`
- **Allowed Priorities**: `low`, `medium`, `high`, `urgent` (defaults to `medium`)
- **Allowed Statuses**: `OPEN`, `IN_PROGRESS`, `RESOLVED`, `CLOSED` (initial status: `OPEN`)
- **Title Length**: 5 to 100 characters inclusive (boundary: 5 and 100 allowed; <5 or >100 rejected)
- **Content-Type**: Requests with bodies must supply `Content-Type: application/json`

---

## Acceptance Criteria

### AC-01: Successful Support Ticket Creation (Happy Path)
- **Given** a client sends a valid ticket creation request
- **When** the client sends a `POST` request to `/api/tickets` with valid `title`, `description`, `category`, and `priority`
- **Then** the system shall create the ticket record
- **And** return HTTP status `201 Created`
- **And** return JSON payload with `success: true`, `message: "Ticket created successfully"`, and `data` containing `id`, `ticket_key`, `title`, `description`, `category`, `priority`, `status` ("OPEN"), `tags`, and `created_at`.

### AC-02: Missing Required Fields Rejection
- **Given** the ticket creation API requires `title`, `description`, and `category`
- **When** any of these required fields is omitted or empty in the request body
- **Then** the system shall reject the request
- **And** return HTTP status `400 Bad Request`
- **And** return an error message indicating that `title, description, and category are required`.

### AC-03: Category Validation
- **Given** allowed ticket categories are strictly `technical`, `billing`, `account`, and `feature`
- **When** the client submits an unrecognized category (e.g., `invalid-category` or `sales`)
- **Then** the system shall reject the request
- **And** return HTTP status `400 Bad Request`
- **And** return an error message indicating `Invalid category. Allowed values: account, billing, feature, technical`.

### AC-04: Priority Validation
- **Given** allowed priority levels are `low`, `medium`, `high`, and `urgent` (defaulting to `medium`)
- **When** the client submits an invalid priority string (e.g., `extreme` or `critical`)
- **Then** the system shall reject the request
- **And** return HTTP status `400 Bad Request`
- **And** return an error message indicating `Invalid priority. Allowed values: high, low, medium, urgent`.

### AC-05: Title Length Boundary Validation
- **Given** ticket title length constraint is between 5 and 100 characters (inclusive)
- **When** a user submits a title with fewer than 5 characters (e.g., "Bug") or greater than 100 characters
- **Then** the system shall reject the request with HTTP status `400 Bad Request`
- **And** titles of exactly 5 characters and exactly 100 characters must be accepted with HTTP status `201 Created`.

### AC-06: Non-JSON Request Rejection
- **Given** `/api/tickets` expects a JSON request body
- **When** the client sends a non-JSON payload or invalid Content-Type (e.g., `application/x-www-form-urlencoded`)
- **Then** the system shall reject the request
- **And** return HTTP status `400 Bad Request` with error message `"Request body must be JSON"`.

### AC-07: Retrieve Existing Ticket by ID
- **Given** a ticket exists with a known numeric ID (e.g., `101`)
- **When** a client sends a `GET` request to `/api/tickets/101`
- **Then** the system shall return HTTP status `200 OK`
- **And** return the full ticket details matching ID 101 with `success: true`.

### AC-08: Retrieve Non-Existent Ticket
- **Given** a ticket ID does not exist in the database (e.g., `9999`)
- **When** a client sends a `GET` request to `/api/tickets/9999`
- **Then** the system shall return HTTP status `404 Not Found`
- **And** return an error message `"Ticket not found"`.

### AC-09: List All Tickets with Optional Filtering
- **Given** tickets exist in the system
- **When** a client sends a `GET` request to `/api/tickets` (with optional query parameters `?category=` and `?status=`)
- **Then** the system shall return HTTP status `200 OK`
- **And** return JSON payload with `success: true`, `total` count, and a `data` array of matching tickets.

### AC-10: Update Ticket Lifecycle Status
- **Given** an existing ticket exists with ID `101`
- **When** a client sends a `PATCH` request to `/api/tickets/101/status` with a valid status payload `{"status": "IN_PROGRESS"}`
- **Then** the system shall update the status and return HTTP status `200 OK` with the updated ticket
- **And** if an invalid status is sent, return HTTP status `400 Bad Request`
- **And** if the ticket does not exist, return HTTP status `404 Not Found`.

---

## Deliberate Code Structure for Agent 24 Stage 5

```text
create_ticket_handler()
    -> validate_ticket_payload()
    -> create_ticket_record()

get_ticket_handler()
    -> get_ticket_by_id()

list_tickets_handler()
    -> list_tickets_records()

update_ticket_status_handler()
    -> update_ticket_status_record()
```
