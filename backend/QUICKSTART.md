# Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL (optional, defaults to SQLite)
- Redis (optional, graceful fallback)

## Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run tests:**
   ```bash
   ./run_tests.sh
   # or
   pytest app/tests/test_auth.py -v
   ```

4. **Start the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at: http://localhost:8000

5. **View API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Quick Test

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePassword123!"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePassword123!"}'

# Refresh token (use refresh_token from login response)
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN_HERE"}'
```

## Using Docker

```bash
# Start all services (API + PostgreSQL + Redis)
docker-compose up

# Run tests in Docker
docker-compose exec api pytest app/tests/test_auth.py -v

# Stop all services
docker-compose down
```

## Environment Variables

Optional environment variables:

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname  # Default: sqlite:///./test.db
export REDIS_URL=redis://localhost:6379/0  # Optional
export SECRET_KEY=your-secret-key-here  # Important for production!
```

## Coverage Report

```bash
pytest --cov=app --cov-report=html app/tests/test_auth.py
# Open htmlcov/index.html in browser
```

## Production Deployment

**Important:** Before deploying to production:

1. Change `SECRET_KEY` in `app/security.py` to a strong random value
2. Set up PostgreSQL database (SQLite is not recommended for production)
3. Set up Redis for token management and rate limiting
4. Enable HTTPS/TLS
5. Configure proper CORS origins
6. Set up logging and monitoring
7. Use environment variables for all sensitive configuration

## Troubleshooting

**Tests failing?**
- Ensure no other process is using the test database
- Clean up: `rm -f test_auth.db *.db`

**Can't connect to Redis?**
- Redis is optional; the app will work without it (with reduced features)
- Install Redis: `apt-get install redis-server` or `brew install redis`

**Port already in use?**
- Change port: `uvicorn app.main:app --port 8001`
