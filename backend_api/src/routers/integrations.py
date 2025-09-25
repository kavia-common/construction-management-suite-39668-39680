from typing import Optional
from fastapi import APIRouter, Header
from pydantic import BaseModel, Field

router = APIRouter()


class WebhookEvent(BaseModel):
    event_type: str = Field(..., description="Event type")
    payload: dict = Field(default_factory=dict, description="Event payload")


# PUBLIC_INTERFACE
@router.post("/webhook", summary="Generic webhook receiver", description="Receives webhook events from external services.", response_model=dict)
def receive_webhook(event: WebhookEvent, x_signature: Optional[str] = Header(None, alias="X-Signature")):
    """This is a public function."""
    # Validate signature if configured
    # For now, accept all and echo
    return {"received": True, "event": event.event_type}


class FinanceSyncRequest(BaseModel):
    provider: str = Field(..., description="Provider name (e.g., quickbooks, xero)")
    since: Optional[str] = Field(None, description="ISO date-time to sync since")


# PUBLIC_INTERFACE
@router.post("/finance/sync", summary="Sync financials", description="Initiate a finance sync with external provider.", response_model=dict)
def sync_finance(payload: FinanceSyncRequest):
    """This is a public function."""
    # Placeholder: Add queue/job creation to process sync
    return {"message": f"Sync initiated for {payload.provider}", "since": payload.since}
