from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Lead(BaseModel):
    id: str = Field(..., description="Lead ID")
    source: str = Field(..., description="Lead source e.g., web, referral")
    name: str = Field(..., description="Contact name")
    email: Optional[str] = Field(None, description="Contact email")
    status: str = Field("new", description="Status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class LeadCreate(BaseModel):
    source: str = Field(..., description="Lead source")
    name: str = Field(..., description="Contact name")
    email: Optional[str] = Field(None, description="Contact email")


# PUBLIC_INTERFACE
@router.get("/leads", summary="List leads", response_model=PaginatedResponse)
def list_leads(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/leads", summary="Create lead", response_model=Lead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate):
    """This is a public function."""
    lid = f"lead_{len(_DB)+1}"
    lead = Lead(id=lid, source=payload.source, name=payload.name, email=payload.email)
    _DB[lid] = lead.model_dump()
    return lead
