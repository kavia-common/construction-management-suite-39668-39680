from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Job(BaseModel):
    id: str = Field(..., description="Job ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Job title")
    status: str = Field("pending", description="Job status")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class JobCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Job title")


class JobUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Job title")
    status: Optional[str] = Field(None, description="Job status")
    assigned_to: Optional[str] = Field(None, description="Assigned user ID")


# PUBLIC_INTERFACE
@router.get("/", summary="List jobs", response_model=PaginatedResponse)
def list_jobs(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create job", response_model=Job, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreate):
    """This is a public function."""
    jid = f"job_{len(_DB)+1}"
    job = Job(id=jid, project_id=payload.project_id, title=payload.title)
    _DB[jid] = job.model_dump()
    return job


# PUBLIC_INTERFACE
@router.put("/{job_id}", summary="Update job", response_model=Job)
def update_job(job_id: str, payload: JobUpdate):
    """This is a public function."""
    if job_id not in _DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    existing = Job(**_DB[job_id])
    updated = existing.model_copy(update={k: v for k, v in payload.model_dump(exclude_unset=True).items()})
    _DB[job_id] = updated.model_dump()
    return updated
