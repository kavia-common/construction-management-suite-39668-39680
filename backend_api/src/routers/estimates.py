from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class EstimateItem(BaseModel):
    description: str = Field(..., description="Line item description")
    quantity: float = Field(..., ge=0, description="Quantity")
    unit_cost: float = Field(..., ge=0, description="Unit cost")


class Estimate(BaseModel):
    id: str = Field(..., description="Estimate ID")
    project_id: Optional[str] = Field(None, description="Associated project ID")
    items: List[EstimateItem] = Field(default_factory=list, description="Estimate items")
    total: float = Field(0, description="Computed total")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class EstimateCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="Associated project ID")
    items: List[EstimateItem] = Field(default_factory=list, description="Estimate items")


# PUBLIC_INTERFACE
@router.get("/", summary="List estimates", response_model=PaginatedResponse)
def list_estimates(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create estimate", response_model=Estimate, status_code=status.HTTP_201_CREATED)
def create_estimate(payload: EstimateCreate):
    """This is a public function."""
    eid = f"est_{len(_DB)+1}"
    total = sum(i.quantity * i.unit_cost for i in payload.items)
    est = Estimate(id=eid, project_id=payload.project_id, items=payload.items, total=total)
    _DB[eid] = est.model_dump()
    return est


# PUBLIC_INTERFACE
@router.get("/{estimate_id}", summary="Get estimate", response_model=Estimate)
def get_estimate(estimate_id: str):
    """This is a public function."""
    if estimate_id not in _DB:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Estimate not found")
    return _DB[estimate_id]
