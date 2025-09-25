from typing import Optional, Dict, Any, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field

import src.core.plaid_client as plaid_client

router = APIRouter()

# In-memory storage for demo/scaffold purposes.
# In an actual implementation, persist to construction_management_db keyed by user_id.
_USER_ITEM_STORE: Dict[str, Dict[str, Any]] = {}
_USER_TRANSACTIONS: Dict[str, List[Dict[str, Any]]] = {}


class LinkTokenRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the authenticated user.")
    products: Optional[List[str]] = Field(default=None, description="Optional list of Plaid products, default: ['transactions'].")


class LinkTokenResponse(BaseModel):
    link_token: str = Field(..., description="Token for initializing Plaid Link.")
    expiration: Optional[str] = Field(None, description="ISO timestamp when the token expires.")


# PUBLIC_INTERFACE
@router.post("/link/token/create", summary="Create Plaid Link token", description="Create a Plaid Link token for initializing the client side Link flow.", response_model=LinkTokenResponse)
def create_link_token(payload: LinkTokenRequest):
    """Create and return a Plaid Link token for the specified user."""
    svc = plaid_client.get_plaid_service()
    try:
        data = svc.create_link_token(user_id=payload.user_id, products=payload.products)
        return LinkTokenResponse(link_token=data.get("link_token", ""), expiration=data.get("expiration"))
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create link token: {ex}")


class PublicTokenExchangeRequest(BaseModel):
    user_id: str = Field(..., description="User id that completed Link.")
    public_token: str = Field(..., description="Public token received from Plaid Link.")


class PublicTokenExchangeResponse(BaseModel):
    access_token: str = Field(..., description="Access token used to access Plaid data.")
    item_id: str = Field(..., description="Plaid item id.")
    message: str = Field(..., description="Status message.")


# PUBLIC_INTERFACE
@router.post("/item/public_token/exchange", summary="Exchange public token", description="Exchange a public_token from Link for an access_token and item_id.", response_model=PublicTokenExchangeResponse)
def exchange_public_token(payload: PublicTokenExchangeRequest):
    """Exchange a public token for an access token and store it for the user."""
    svc = plaid_client.get_plaid_service()
    try:
        data = svc.exchange_public_token(payload.public_token)
        access_token = data.get("access_token")
        item_id = data.get("item_id")
        if not access_token or not item_id:
            raise ValueError("Missing access_token or item_id in Plaid response")
        # Store by user
        _USER_ITEM_STORE[payload.user_id] = {
            "access_token": access_token,
            "item_id": item_id,
            "updated_at": datetime.utcnow().isoformat(),
        }
        return PublicTokenExchangeResponse(access_token=access_token, item_id=item_id, message="Token exchanged and stored.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Token exchange failed: {ex}")


class AccountsRequest(BaseModel):
    user_id: str = Field(..., description="User id owning the Plaid item.")


class Account(BaseModel):
    account_id: str = Field(..., description="Plaid account id")
    name: Optional[str] = Field(None, description="Account name")
    official_name: Optional[str] = Field(None, description="Official account name")
    subtype: Optional[str] = Field(None, description="Account subtype")
    type: Optional[str] = Field(None, description="Account type")
    mask: Optional[str] = Field(None, description="Masked number")


class AccountsResponse(BaseModel):
    accounts: List[Account] = Field(default_factory=list, description="List of accounts.")


# PUBLIC_INTERFACE
@router.post("/accounts/get", summary="Get accounts", description="Retrieve accounts for the user's Plaid item.", response_model=AccountsResponse)
def get_accounts(payload: AccountsRequest):
    """Fetch accounts from Plaid for the stored access token."""
    svc = get_plaid_service()
    user_rec = _USER_ITEM_STORE.get(payload.user_id)
    if not user_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Plaid item configured for this user.")
    try:
        data = svc.get_accounts(user_rec["access_token"])
        accounts_raw = data.get("accounts", [])
        accounts = []
        for a in accounts_raw:
            accounts.append(Account(
                account_id=a.get("account_id"),
                name=a.get("name"),
                official_name=a.get("official_name"),
                subtype=(a.get("subtype") if isinstance(a.get("subtype"), str) else a.get("subtype", None)),
                type=(a.get("type") if isinstance(a.get("type"), str) else a.get("type", None)),
                mask=a.get("mask"),
            ))
        return AccountsResponse(accounts=accounts)
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to get accounts: {ex}")


class TransactionsSyncRequest(BaseModel):
    user_id: str = Field(..., description="User id owning the Plaid item.")
    cursor: Optional[str] = Field(None, description="Cursor for transactions/sync; pass None for initial sync.")
    count: int = Field(100, ge=1, le=500, description="Number of records to request per page.")


class Transaction(BaseModel):
    transaction_id: str = Field(..., description="Plaid transaction id")
    account_id: str = Field(..., description="Account id")
    name: Optional[str] = Field(None, description="Merchant or description")
    amount: float = Field(..., description="Amount (positive for debit)")
    date: Optional[str] = Field(None, description="ISO date")
    pending: Optional[bool] = Field(None, description="Pending flag")
    category: Optional[List[str]] = Field(None, description="Plaid category array")
    merchant_name: Optional[str] = Field(None, description="Merchant name")


class TransactionsSyncResponse(BaseModel):
    added: List[Transaction] = Field(default_factory=list, description="Newly added transactions")
    modified: List[Transaction] = Field(default_factory=list, description="Modified transactions")
    removed: List[Dict[str, Any]] = Field(default_factory=list, description="Removed transactions (id only)")
    next_cursor: Optional[str] = Field(None, description="Cursor for next call")
    has_more: bool = Field(False, description="If more results available")


# PUBLIC_INTERFACE
@router.post("/transactions/sync", summary="Sync transactions", description="Fetch transactions using Plaid transactions/sync and store them for the user.", response_model=TransactionsSyncResponse)
def sync_transactions(payload: TransactionsSyncRequest):
    """Sync transactions and persist in-memory for the user."""
    svc = get_plaid_service()
    user_rec = _USER_ITEM_STORE.get(payload.user_id)
    if not user_rec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Plaid item configured for this user.")
    try:
        data = svc.get_transactions_sync(access_token=user_rec["access_token"], cursor=payload.cursor, count=payload.count)
        # Convert added/modified into our Transaction model and store
        added_raw = data.get("added", [])
        modified_raw = data.get("modified", [])
        removed = data.get("removed", [])
        tx_store = _USER_TRANSACTIONS.setdefault(payload.user_id, [])

        def convert_tx(t: Dict[str, Any]) -> Transaction:
            return Transaction(
                transaction_id=t.get("transaction_id", t.get("transaction", t.get("id", ""))),
                account_id=t.get("account_id", ""),
                name=t.get("name"),
                amount=float(t.get("amount", 0.0)),
                date=t.get("date"),
                pending=t.get("pending"),
                category=t.get("category"),
                merchant_name=t.get("merchant_name"),
            )

        added = [convert_tx(t) for t in added_raw]
        modified = [convert_tx(t) for t in modified_raw]

        # naive in-memory upsert
        existing_by_id = {t["transaction_id"]: i for i, t in enumerate(tx_store) if "transaction_id" in t}
        for t in added:
            if t.transaction_id not in existing_by_id:
                tx_store.append(t.model_dump())
        for t in modified:
            if t.transaction_id in existing_by_id:
                idx = existing_by_id[t.transaction_id]
                tx_store[idx] = t.model_dump()

        return TransactionsSyncResponse(
            added=added,
            modified=modified,
            removed=removed or [],
            next_cursor=data.get("next_cursor"),
            has_more=bool(data.get("has_more", False)),
        )
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to sync transactions: {ex}")


# PUBLIC_INTERFACE
@router.get("/transactions", summary="List stored transactions", description="List transactions stored for the user (from previous sync).", response_model=List[Transaction])
def list_transactions(user_id: str = Query(..., description="User id for which to list transactions"), limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    """Return previously synced transactions from in-memory storage."""
    items = _USER_TRANSACTIONS.get(user_id, [])
    sliced = items[offset: offset + limit]
    return [Transaction(**t) for t in sliced]
