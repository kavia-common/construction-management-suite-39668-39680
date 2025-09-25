from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Proposal(BaseModel):
    id: str = Field(..., description="Proposal ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Proposal title")
    amount: float = Field(0, description="Proposal amount")
    status: str = Field("draft", description="Status: draft/sent/accepted/rejected")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class ProposalCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Title")
    amount: float = Field(0, description="Amount")


# PUBLIC_INTERFACE
@router.get("/", summary="List proposals", response_model=PaginatedResponse)
def list_proposals(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create proposal", response_model=Proposal, status_code=status.HTTP_201_CREATED)
def create_proposal(payload: ProposalCreate):
    """This is a public function."""
    pid = f"prop_{len(_DB)+1}"
    prop = Proposal(id=pid, project_id=payload.project_id, title=payload.title, amount=payload.amount)
    _DB[pid] = prop.model_dump()
    return prop
