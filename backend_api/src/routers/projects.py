from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

from src.models.common import PaginatedResponse

router = APIRouter()


class Project(BaseModel):
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    client_name: str = Field(..., description="Client name")
    status: str = Field(..., description="Status e.g., planning, active, closed")
    budget: float = Field(0, description="Budget amount")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    client_name: str = Field(..., description="Client name")
    budget: float = Field(0, description="Budget amount")


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Project name")
    client_name: Optional[str] = Field(None, description="Client name")
    budget: Optional[float] = Field(None, description="Budget amount")
    status: Optional[str] = Field(None, description="Project status")


# In-memory store for scaffold purposes
_DB: dict = {}


# PUBLIC_INTERFACE
@router.get("/", summary="List projects", description="Return a paginated list of projects.", response_model=PaginatedResponse)
def list_projects(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create project", description="Create a new project.", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate):
    """This is a public function."""
    pid = f"prj_{len(_DB)+1}"
    project = Project(id=pid, name=payload.name, client_name=payload.client_name, budget=payload.budget, status="planning")
    _DB[pid] = project.model_dump()
    return project


# PUBLIC_INTERFACE
@router.get("/{project_id}", summary="Get project", description="Fetch a project by ID.", response_model=Project)
def get_project(project_id: str):
    """This is a public function."""
    if project_id not in _DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return _DB[project_id]


# PUBLIC_INTERFACE
@router.put("/{project_id}", summary="Update project", description="Update a project by ID.", response_model=Project)
def update_project(project_id: str, payload: ProjectUpdate):
    """This is a public function."""
    if project_id not in _DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    existing = Project(**_DB[project_id])
    updated = existing.model_copy(update={k: v for k, v in payload.model_dump(exclude_unset=True).items()})
    _DB[project_id] = updated.model_dump()
    return updated


# PUBLIC_INTERFACE
@router.delete("/{project_id}", summary="Delete project", description="Delete a project by ID.", response_model=dict, status_code=status.HTTP_200_OK)
def delete_project(project_id: str):
    """This is a public function."""
    if project_id not in _DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    del _DB[project_id]
    return {"message": "Deleted"}
