# Authentication API

FastAPI-based authentication API with JWT tokens, bcrypt password hashing, and Redis-backed refresh token management.

## Features

- **User Registration** (`POST /api/auth/register`): Create new user accounts with email validation and secure password hashing
- **User Login** (`POST /api/auth/login`): Authenticate users and issue JWT tokens
- **Token Refresh** (`POST /api/auth/refresh`): Refresh access tokens using refresh tokens with automatic rotation
- **Security Features**:
  - Bcrypt password hashing
  - JWT access and refresh tokens
  - Refresh token fingerprinting in Redis
  - Token rotation on refresh
  - Rate limiting stubs for brute-force protection
  - Password never logged or exposed
- **Metadata**: All responses include version and timestamp metadata

## Installation

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export DATABASE_URL=sqlite:///./test.db  # or PostgreSQL URL
export REDIS_URL=redis://localhost:6379/0  # optional
```

3. Run the server:
```bash
uvicorn app.main:app --reload
```

### Docker Compose

```bash
docker-compose up
```

This will start:
- API server on port 8000
- PostgreSQL database on port 5432
- Redis on port 6379

## Running Tests

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=app/routers/auth.py --cov-report=html
```

### Run specific test class:
```bash
pytest app/tests/test_auth.py::TestRegistration -v
```

## API Endpoints

### POST /api/auth/register

Register a new user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJ...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

### POST /api/auth/login

Authenticate a user.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJ...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

### POST /api/auth/refresh

Refresh access token.

**Request:**
```json
{
  "refresh_token": "eyJ..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJ...",
    "token_type": "bearer",
    "expires_in": 900,
    "refresh_token": "eyJ...",
    "refresh_expires_in": 604800
  },
  "metadata": {
    "version": "1.0.0",
    "timestamp": "2024-01-01T12:00:00.000000"
  }
}
```

## Test Coverage

Run tests with coverage to ensure ≥80% coverage:

```bash
pytest --cov=app/routers/auth.py --cov-report=term-missing
```

## Security Notes

- Passwords are hashed using bcrypt before storage
- JWT tokens use HS256 algorithm (change SECRET_KEY in production)
- Refresh token fingerprints stored in Redis with automatic expiration
- Rate limiting implemented for brute-force protection
- Passwords are never logged or exposed in responses
- Token rotation on refresh for enhanced security

## Architecture

- **Models** (`models.py`): SQLAlchemy User model with helper queries
- **Security** (`security.py`): JWT creation/verification, password hashing, rate limiting
- **Schemas** (`schemas.py`): Pydantic request/response models with metadata
- **Database** (`database.py`): Database connection and session management
- **Redis** (`redis_client.py`): Redis client for token fingerprints and rate limiting
- **Router** (`routers/auth.py`): Auth endpoints implementation
- **Tests** (`tests/test_auth.py`): Comprehensive test suite with ≥80% coverage
