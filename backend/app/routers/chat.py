from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import create_response_envelope

router = APIRouter()


@router.get("/")
async def list_chat_sessions(db: AsyncSession = Depends(get_db)):
    """List all chat sessions for current user"""
    return create_response_envelope(
        data={"message": "List chat sessions endpoint - to be implemented"}
    )


@router.post("/")
async def create_chat_session(db: AsyncSession = Depends(get_db)):
    """Create a new chat session"""
    return create_response_envelope(
        data={"message": "Create chat session endpoint - to be implemented"}
    )


@router.get("/{session_id}")
async def get_chat_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific chat session"""
    return create_response_envelope(
        data={"message": f"Get chat session {session_id} endpoint - to be implemented"}
    )


@router.post("/{session_id}/messages")
async def send_message(session_id: int, db: AsyncSession = Depends(get_db)):
    """Send a message in a chat session"""
    return create_response_envelope(
        data={"message": f"Send message to session {session_id} endpoint - to be implemented"}
    )


@router.delete("/{session_id}")
async def delete_chat_session(session_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a chat session"""
    return create_response_envelope(
        data={"message": f"Delete chat session {session_id} endpoint - to be implemented"}
    )