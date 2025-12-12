# Authentication API Contract

## Base URL
```
http://localhost:8000
```

## Common Response Structure

All successful responses follow this format:

```typescript
{
  success: boolean;
  message: string;
  data?: TokenResponse;
  metadata: {
    version: string;      // API version (e.g., "1.0.0")
    timestamp: string;    // ISO 8601 timestamp
  }
}
```

## Token Response Structure

```typescript
{
  access_token: string;         // JWT access token
  token_type: string;           // Always "bearer"
  expires_in: number;           // Seconds until access token expires (900)
  refresh_token?: string;       // JWT refresh token (optional)
  refresh_expires_in?: number;  // Seconds until refresh token expires (604800)
}
```

## Endpoints

### 1. Register User

**Endpoint**: `POST /api/auth/register`

**Description**: Create a new user account

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Schema**:
- `email` (string, required): Valid email address
- `password` (string, required): Minimum 8 characters, maximum 100 characters

**Success Response** (201 Created):
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

**Error Responses**:

- **400 Bad Request** - Email already registered:
  ```json
  {
    "detail": "Email already registered"
  }
  ```

- **422 Unprocessable Entity** - Validation error:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "email"],
        "msg": "value is not a valid email address",
        "type": "value_error.email"
      }
    ]
  }
  ```

- **429 Too Many Requests** - Rate limit exceeded:
  ```json
  {
    "detail": "Too many registration attempts. Please try again later."
  }
  ```

**Rate Limit**: 5 attempts per hour per email

---

### 2. Login User

**Endpoint**: `POST /api/auth/login`

**Description**: Authenticate a user and receive tokens

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Request Schema**:
- `email` (string, required): Valid email address
- `password` (string, required): User's password

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

**Error Responses**:

- **401 Unauthorized** - Invalid credentials:
  ```json
  {
    "detail": "Invalid email or password"
  }
  ```

- **403 Forbidden** - Account inactive:
  ```json
  {
    "detail": "User account is inactive"
  }
  ```

- **422 Unprocessable Entity** - Validation error:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "email"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

- **429 Too Many Requests** - Rate limit exceeded:
  ```json
  {
    "detail": "Too many login attempts. Please try again later."
  }
  ```

**Rate Limit**: 10 attempts per 10 minutes per email

---

### 3. Refresh Token

**Endpoint**: `POST /api/auth/refresh`

**Description**: Refresh access token using a valid refresh token. Implements token rotation - a new refresh token is issued.

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Schema**:
- `refresh_token` (string, required): Valid JWT refresh token

**Success Response** (200 OK):
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

**Error Responses**:

- **401 Unauthorized** - Invalid or expired token:
  ```json
  {
    "detail": "Invalid or expired refresh token"
  }
  ```

- **401 Unauthorized** - Wrong token type (access token used):
  ```json
  {
    "detail": "Invalid or expired refresh token"
  }
  ```

- **401 Unauthorized** - Token revoked:
  ```json
  {
    "detail": "Refresh token has been revoked"
  }
  ```

- **401 Unauthorized** - User not found:
  ```json
  {
    "detail": "User not found"
  }
  ```

- **403 Forbidden** - Account inactive:
  ```json
  {
    "detail": "User account is inactive"
  }
  ```

- **422 Unprocessable Entity** - Validation error:
  ```json
  {
    "detail": [
      {
        "loc": ["body", "refresh_token"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

---

## JWT Token Structure

### Access Token Payload
```json
{
  "sub": "1",                    // User ID
  "email": "user@example.com",   // User email
  "exp": 1735560986,            // Expiration timestamp
  "type": "access",             // Token type
  "jti": "unique-token-id"      // Unique token identifier
}
```

### Refresh Token Payload
```json
{
  "sub": "1",                // User ID
  "exp": 1736164894,        // Expiration timestamp
  "type": "refresh",        // Token type
  "jti": "unique-token-id"  // Unique token identifier
}
```

## Token Expiration

- **Access Token**: 15 minutes (900 seconds)
- **Refresh Token**: 7 days (604800 seconds)

## Security Features

1. **Password Hashing**: All passwords hashed with bcrypt
2. **Token Fingerprinting**: Refresh tokens fingerprinted and stored in Redis
3. **Token Rotation**: New refresh token issued on every refresh
4. **Token Types**: Separate access and refresh tokens with type checking
5. **Unique JTI**: Each token has a unique identifier
6. **Rate Limiting**: Protection against brute-force attacks
7. **No Password Logging**: Passwords never appear in logs or responses

## Using the Tokens

Include the access token in the `Authorization` header for protected endpoints:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Error Response Format

All errors follow FastAPI's standard format:

```json
{
  "detail": "Error message"
}
```

Or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

## Health Check Endpoints

### Health Check
**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy"
}
```

### Root
**Endpoint**: `GET /`

**Response**:
```json
{
  "message": "Auth API",
  "version": "1.0.0"
}
```

## OpenAPI Documentation

Interactive API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Example Usage

### Complete Flow (cURL)

```bash
# 1. Register
REGISTER_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePassword123!"}')

echo $REGISTER_RESPONSE | jq .

# 2. Login
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePassword123!"}')

REFRESH_TOKEN=$(echo $LOGIN_RESPONSE | jq -r .data.refresh_token)
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r .data.access_token)

echo "Access Token: $ACCESS_TOKEN"
echo "Refresh Token: $REFRESH_TOKEN"

# 3. Refresh
REFRESH_RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

echo $REFRESH_RESPONSE | jq .
```

### Example Usage (Python)

```python
import httpx

BASE_URL = "http://localhost:8000"

# Register
response = httpx.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
)
data = response.json()
print(f"Registered: {data['success']}")

# Login
response = httpx.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "email": "test@example.com",
        "password": "SecurePassword123!"
    }
)
data = response.json()
access_token = data["data"]["access_token"]
refresh_token = data["data"]["refresh_token"]

# Refresh
response = httpx.post(
    f"{BASE_URL}/api/auth/refresh",
    json={"refresh_token": refresh_token}
)
data = response.json()
new_access_token = data["data"]["access_token"]
new_refresh_token = data["data"]["refresh_token"]

print(f"New tokens obtained: {data['success']}")
```

## Notes

- All timestamps are in UTC
- Tokens are stateless JWT tokens
- Redis is optional but recommended for production
- PostgreSQL recommended for production (SQLite used by default)
- HTTPS should be enforced in production
