from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import Request
from app.settings import settings


def create_response_envelope(data: Any = None, error: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a standardized response envelope with version and timestamp
    """
    envelope = {
        "version": settings.api_version,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    if data is not None:
        envelope["data"] = data
    
    if error is not None:
        envelope["error"] = error
    
    if meta is not None:
        envelope["meta"] = meta
    
    return envelope


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0]
    return request.client.host if request.client else "unknown"


def get_user_agent(request: Request) -> str:
    """Extract user agent from request"""
    return request.headers.get("user-agent", "unknown")


async def health_check():
    """
    Health check endpoint data
    """
    return create_response_envelope(data={
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug
    })