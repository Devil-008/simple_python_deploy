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
