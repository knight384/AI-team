# Full-Stack Application

This repository contains a full-stack application with a React frontend and FastAPI backend.

## Repository Structure

```
/
├── frontend/          # React + Vite frontend application
├── backend/           # FastAPI backend application
├── docker-compose.yml # Docker services configuration
└── README.md         # This file
```

## Frontend (React + Vite)

The frontend is a React 18 application with TypeScript, built using Vite. It includes:

- **Framework**: React 18 with TypeScript
- **Styling**: TailwindCSS via CDN
- **Animations**: Framer Motion
- **Routing**: React Router DOM
- **3D Graphics**: React Three Fiber & Drei
- **Charts**: Recharts
- **Icons**: Lucide React

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Frontend Environment Variables

Create a `.env` file in the frontend directory:

```bash
VITE_GEMINI_API_KEY=your-gemini-api-key-here
```

## Backend (FastAPI)

The backend is a FastAPI application with PostgreSQL and Redis. It includes:

- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy async
- **ORM**: SQLAlchemy with Alembic migrations
- **Caching**: Redis
- **Authentication**: JWT with bcrypt
- **API Design**: RESTful with consistent response envelope

### Backend Setup

1. **Using Docker Compose (Recommended)**

```bash
# Start all services (PostgreSQL, Redis, and optionally backend)
docker-compose up -d

# Run database migrations
cd backend
alembic upgrade head

# Start the backend (if not using docker-compose for backend)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. **Manual Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL and Redis (using docker-compose or manually)
docker-compose up -d postgres redis

# Run migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Migrations

```bash
cd backend

# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration status
alembic current
alembic history
```

### Backend Environment Variables

Create a `.env` file in the backend directory based on `.env.example`:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

```bash
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/mydb
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-super-secret-jwt-key-here
OPENAI_API_KEY=your-openai-api-key-here
API_VERSION=v1
ENVIRONMENT=development
DEBUG=true
```

### API Endpoints

Once running, the backend will be available at `http://localhost:8000`

- **Health Check**: `GET /health`
- **API Documentation**: `GET /docs`
- **Auth Routes**: `GET /api/v1/auth/*`
- **Chat Routes**: `GET /api/v1/chat/*`
- **Concepts Routes**: `GET /api/v1/concepts/*`
- **Projects Routes**: `GET /api/v1/projects/*`
- **Code Routes**: `GET /api/v1/code/*`

### Database Models

The backend includes the following main models:

- **Users**: User accounts with authentication
- **Concepts**: Knowledge concepts with embeddings
- **Projects**: User projects linked to concepts
- **Conversations**: Chat conversations
- **UserProgress**: Progress tracking for projects

All models include proper relationships and use PostgreSQL-specific features like JSONB for complex data structures.

## Docker Services

The `docker-compose.yml` file includes:

- **PostgreSQL 15**: Main database on port 5432
- **Redis 7**: Caching layer on port 6379
- **FastAPI Backend**: Optional development service on port 8000

## Development Workflow

1. **Frontend Development**: 
   - Start frontend with `npm run dev` in `/frontend`
   - Access at `http://localhost:5173`

2. **Backend Development**:
   - Start services with `docker-compose up -d postgres redis`
   - Run migrations with `alembic upgrade head`
   - Start backend with `uvicorn app.main:app --reload`

3. **Database Changes**:
   - Modify models in `backend/app/models.py`
   - Generate migration: `alembic revision --autogenerate -m "description"`
   - Apply migration: `alembic upgrade head`

## Production Deployment

For production deployment:

1. **Update Environment Variables**: Set secure secrets and production URLs
2. **Database**: Use production PostgreSQL instance
3. **Docker**: Build and deploy with proper configuration
4. **Frontend**: Build with `npm run build` and serve static files
5. **Backend**: Use production ASGI server (Gunicorn + Uvicorn workers)

## API Response Format

All API responses follow a consistent envelope format:

```json
{
  "version": "v1",
  "timestamp": "2024-12-12T08:00:00.000Z",
  "data": { ... },      // Response data (when successful)
  "error": null,         // Error message (when failed)
  "meta": { ... }        // Additional metadata (optional)
}
```