from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Invoice(BaseModel):
    id: str = Field(..., description="Invoice ID")
    project_id: Optional[str] = Field(None, description="Project ID")
    amount: float = Field(0, description="Invoice amount")
    due_date: Optional[datetime] = Field(None, description="Due date")
    status: str = Field("unpaid", description="Status: unpaid/paid/overdue")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Created timestamp")


class InvoiceCreate(BaseModel):
    project_id: Optional[str] = Field(None, description="Project ID")
    amount: float = Field(0, description="Amount")
    due_date: Optional[datetime] = Field(None, description="Due date")


# PUBLIC_INTERFACE
@router.get("/", summary="List invoices", response_model=PaginatedResponse)
def list_invoices(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create invoice", response_model=Invoice, status_code=status.HTTP_201_CREATED)
def create_invoice(payload: InvoiceCreate):
    """This is a public function."""
    iid = f"inv_{len(_DB)+1}"
    invoice = Invoice(id=iid, project_id=payload.project_id, amount=payload.amount, due_date=payload.due_date)
    _DB[iid] = invoice.model_dump()
    return invoice
