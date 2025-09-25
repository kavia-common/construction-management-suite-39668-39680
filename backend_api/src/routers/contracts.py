from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Contract(BaseModel):
    id: str = Field(..., description="Contract ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Contract title")
    body: str = Field(..., description="Contract content/markdown")
    signed: bool = Field(False, description="Signed status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class ContractCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID")
    title: str = Field(..., description="Title")
    body: str = Field(..., description="Content/markdown")


# PUBLIC_INTERFACE
@router.get("/", summary="List contracts", response_model=PaginatedResponse)
def list_contracts(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create contract", response_model=Contract, status_code=status.HTTP_201_CREATED)
def create_contract(payload: ContractCreate):
    """This is a public function."""
    cid = f"ctr_{len(_DB)+1}"
    contract = Contract(id=cid, project_id=payload.project_id, title=payload.title, body=payload.body)
    _DB[cid] = contract.model_dump()
    return contract
