from datetime import datetime
from typing import Optional
from fastapi import APIRouter, status, Query
from pydantic import BaseModel, Field
from src.models.common import PaginatedResponse

router = APIRouter()

_DB: dict = {}


class Receipt(BaseModel):
    id: str = Field(..., description="Receipt ID")
    invoice_id: Optional[str] = Field(None, description="Invoice ID")
    amount: float = Field(0, description="Amount received")
    received_at: datetime = Field(default_factory=datetime.utcnow, description="Received timestamp")


class ReceiptCreate(BaseModel):
    invoice_id: Optional[str] = Field(None, description="Invoice ID")
    amount: float = Field(..., ge=0, description="Amount")


# PUBLIC_INTERFACE
@router.get("/", summary="List receipts", response_model=PaginatedResponse)
def list_receipts(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=200)):
    """This is a public function."""
    items = list(_DB.values())
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items[start:end])


# PUBLIC_INTERFACE
@router.post("/", summary="Create receipt", response_model=Receipt, status_code=status.HTTP_201_CREATED)
def create_receipt(payload: ReceiptCreate):
    """This is a public function."""
    rid = f"rcp_{len(_DB)+1}"
    receipt = Receipt(id=rid, invoice_id=payload.invoice_id, amount=payload.amount)
    _DB[rid] = receipt.model_dump()
    return receipt
