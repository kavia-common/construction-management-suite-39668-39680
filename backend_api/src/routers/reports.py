from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class SummaryReport(BaseModel):
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    total_projects: int = Field(..., description="Total projects")
    total_invoices: int = Field(..., description="Total invoices")
    total_revenue: float = Field(..., description="Total revenue sum")


# PUBLIC_INTERFACE
@router.get("/summary", summary="Summary report", description="Return high-level counts and totals.", response_model=SummaryReport)
def summary_report():
    """This is a public function."""
    # Placeholder values; replace with real queries in integration
    return SummaryReport(total_projects=5, total_invoices=12, total_revenue=123456.78)
