from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.db import init_db, close_db, init_redis
from app.api.deps import create_response_envelope, health_check
from app.routers import auth, chat, concepts, projects, code

# Global app instance
app = FastAPI(title="API Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await init_redis()
    yield
    # Shutdown
    await close_db()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return create_response_envelope(data=await health_check())


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(concepts.router, prefix="/api/v1/concepts", tags=["concepts"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(code.router, prefix="/api/v1/code", tags=["code"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)