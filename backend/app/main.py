from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routers import auth
from .database import init_db
from .redis_client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown."""
    # Startup
    init_db()
    await redis_client.connect()
    yield
    # Shutdown
    await redis_client.close()


app = FastAPI(
    title="Auth API",
    description="Authentication API with JWT tokens",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Auth API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
