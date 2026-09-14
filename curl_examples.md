# cURL Examples

## Login

```bash
curl -X POST http://localhost:5001/api/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"manas\",\"password\":\"password123\"}"
```

## Get User

```bash
curl http://localhost:5001/api/user ^
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Invalid Login

```bash
curl -X POST http://localhost:5001/api/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"manas\",\"password\":\"wrong\"}"
```

## Missing Token

```bash
curl http://localhost:5001/api/user
```

## Create Support Ticket (Valid)

```bash
curl -X POST http://localhost:5001/api/tickets ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Database connection pool exhausted\",\"description\":\"Backend database pool hits limit during peak hours\",\"category\":\"technical\",\"priority\":\"high\"}"
```

## Create Support Ticket (Validation Error - Missing Fields)

```bash
curl -X POST http://localhost:5001/api/tickets ^
  -H "Content-Type: application/json" ^
  -d "{\"title\":\"Short\"}"
```

## Get Ticket by ID

```bash
curl http://localhost:5001/api/tickets/101
```

## List All Tickets

```bash
curl http://localhost:5001/api/tickets
```

## List Tickets with Filters (Category & Status)

```bash
curl "http://localhost:5001/api/tickets?category=technical&status=OPEN"
```

## Update Ticket Status (PATCH)

```bash
curl -X PATCH http://localhost:5001/api/tickets/101/status ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"IN_PROGRESS\"}"
```

