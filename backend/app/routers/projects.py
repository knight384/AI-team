from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.api.deps import create_response_envelope

router = APIRouter()


@router.get("/")
async def list_projects(db: AsyncSession = Depends(get_db)):
    """List all projects"""
    return create_response_envelope(
        data={"message": "List projects endpoint - to be implemented"}
    )


@router.get("/{project_id}")
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get a specific project"""
    return create_response_envelope(
        data={"message": f"Get project {project_id} endpoint - to be implemented"}
    )


@router.post("/")
async def create_project(db: AsyncSession = Depends(get_db)):
    """Create a new project"""
    return create_response_envelope(
        data={"message": "Create project endpoint - to be implemented"}
    )


@router.put("/{project_id}")
async def update_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Update a project"""
    return create_response_envelope(
        data={"message": f"Update project {project_id} endpoint - to be implemented"}
    )


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a project"""
    return create_response_envelope(
        data={"message": f"Delete project {project_id} endpoint - to be implemented"}
    )


@router.get("/{project_id}/progress")
async def get_project_progress(project_id: int, db: AsyncSession = Depends(get_db)):
    """Get project progress"""
    return create_response_envelope(
        data={"message": f"Get project {project_id} progress endpoint - to be implemented"}
    )


@router.put("/{project_id}/progress")
async def update_project_progress(project_id: int, db: AsyncSession = Depends(get_db)):
    """Update project progress"""
    return create_response_envelope(
        data={"message": f"Update project {project_id} progress endpoint - to be implemented"}
    )