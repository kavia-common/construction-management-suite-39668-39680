# Plaid Integration (Backend API)

This backend integrates with Plaid to access banking/finance data. It provides endpoints for Plaid Link initialization, public token exchange, account retrieval, and transaction syncing.

Environment variables (required):
- PLAID_CLIENT_ID
- PLAID_SECRET

Optional:
- PLAID_ENV (sandbox | development | production, default sandbox)
- PLAID_HOST (override host, default based on PLAID_ENV)
- APP_NAME (displayed in Link creation, defaults to "Construction Management Suite")

Endpoints (under /plaid):
- POST /plaid/link/token/create
  - body: { user_id: string, products?: string[] }
  - returns: { link_token, expiration }
- POST /plaid/item/public_token/exchange
  - body: { user_id: string, public_token: string }
  - stores access_token mapped to user_id
  - returns: { access_token, item_id, message }
- POST /plaid/accounts/get
  - body: { user_id: string }
  - returns Plaid accounts for the stored access token
- POST /plaid/transactions/sync
  - body: { user_id: string, cursor?: string, count?: number }
  - uses transactions/sync; persists in-memory for demo
  - returns added/modified/removed and next_cursor/has_more
- GET /plaid/transactions?user_id=...&limit=100&offset=0
  - returns previously synced transactions from memory

Notes
- This scaffold uses in-memory storage for tokens and transactions. Replace with persistence to construction_management_db in production.
- If Plaid SDK or credentials are not configured, endpoints return mock responses for development.

Run locally
1) Create .env from .env.example and set PLAID_* values.
2) pip install -r requirements.txt
3) uvicorn src.api.main:app --reload --port 3001
4) Visit /docs to try the endpoints.
