from typing import Optional, Dict, Any, List
import os
import logging
from datetime import date, timedelta

from pydantic import BaseModel, Field

# Lazy import to avoid hard dependency during scaffolding
try:
    from plaid.api import plaid_api  # type: ignore
    from plaid.model.country_code import CountryCode  # type: ignore
    from plaid.model.link_token_create_request import LinkTokenCreateRequest  # type: ignore
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser  # type: ignore
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest  # type: ignore
    from plaid.model.accounts_get_request import AccountsGetRequest  # type: ignore
    from plaid.model.transactions_sync_request import TransactionsSyncRequest  # type: ignore
    from plaid.model.products import Products  # type: ignore
    from plaid import Configuration, ApiClient  # type: ignore
except Exception:
    plaid_api = None
    CountryCode = None
    LinkTokenCreateRequest = None
    LinkTokenCreateRequestUser = None
    ItemPublicTokenExchangeRequest = None
    AccountsGetRequest = None
    TransactionsSyncRequest = None
    Products = None
    Configuration = None
    ApiClient = None


logger = logging.getLogger(__name__)


class PlaidSettings(BaseModel):
    """Settings specific to Plaid loaded from environment variables."""
    client_id: str = Field(default=os.getenv("PLAID_CLIENT_ID", ""))
    secret: str = Field(default=os.getenv("PLAID_SECRET", ""))
    env: str = Field(default=os.getenv("PLAID_ENV", "sandbox"))
    # Advanced: some SDKs use direct host override
    host: Optional[str] = Field(default=os.getenv("PLAID_HOST", None))
    # App info
    app_name: str = Field(default=os.getenv("APP_NAME", "Construction Management Suite"))


class PlaidService:
    """Wrapper around Plaid SDK providing helper methods."""
    def __init__(self, settings: PlaidSettings) -> None:
        self.settings = settings
        self._client: Optional["plaid_api.PlaidApi"] = None

    def is_configured(self) -> bool:
        return bool(plaid_api and self.settings.client_id and self.settings.secret)

    def _get_base_url(self) -> str:
        # Map env to base URL if host not given
        if self.settings.host:
            return self.settings.host
        env = (self.settings.env or "sandbox").lower()
        if env == "production":
            return "https://production.plaid.com"
        if env == "development":
            return "https://development.plaid.com"
        return "https://sandbox.plaid.com"

    def client(self):
        """Initialize and return Plaid API client instance."""
        if self._client is not None:
            return self._client
        if not self.is_configured():
            raise RuntimeError("Plaid not configured or plaid sdk missing.")
        configuration = Configuration(
            host=self._get_base_url(),
            api_key={
                "PLAID-CLIENT-ID": self.settings.client_id,
                "PLAID-SECRET": self.settings.secret,
            },
        )
        api_client = ApiClient(configuration)
        self._client = plaid_api.PlaidApi(api_client)
        return self._client

    # PUBLIC_INTERFACE
    def create_link_token(self, user_id: str, products: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a Plaid Link token for the given user."""
        if not self.is_configured():
            # Return mock for scaffolding
            return {"link_token": "mock-link-token", "expiration": (date.today() + timedelta(days=1)).isoformat()}
        try:
            _products = products or ["transactions"]
            # Convert to SDK enum when available
            sdk_products = []
            if Products:
                mapping = {
                    "transactions": Products("transactions"),
                    "auth": Products("auth"),
                    "identity": Products("identity"),
                }
                for p in _products:
                    if p in mapping:
                        sdk_products.append(mapping[p])
            else:
                sdk_products = _products  # type: ignore

            # Country codes required by Plaid
            if CountryCode:
                country_codes = [CountryCode("US")]
            else:
                country_codes = ["US"]  # type: ignore

            user = LinkTokenCreateRequestUser(client_user_id=user_id) if LinkTokenCreateRequestUser else {"client_user_id": user_id}
            req = LinkTokenCreateRequest(
                user=user,
                client_name=self.settings.app_name,
                products=sdk_products,
                country_codes=country_codes,
                language="en",
            ) if LinkTokenCreateRequest else {
                "user": user,
                "client_name": self.settings.app_name,
                "products": sdk_products,
                "country_codes": country_codes,
                "language": "en",
            }

            response = self.client().link_token_create(req)
            return response.to_dict()
        except Exception:
            logger.exception("Failed to create link token")
            raise

    # PUBLIC_INTERFACE
    def exchange_public_token(self, public_token: str) -> Dict[str, Any]:
        """Exchange public token for access token and item id."""
        if not self.is_configured():
            return {"access_token": "mock-access", "item_id": "mock-item"}
        try:
            req = ItemPublicTokenExchangeRequest(public_token=public_token) if ItemPublicTokenExchangeRequest else {"public_token": public_token}
            resp = self.client().item_public_token_exchange(req)
            return resp.to_dict()
        except Exception:
            logger.exception("Failed to exchange public token")
            raise

    # PUBLIC_INTERFACE
    def get_accounts(self, access_token: str) -> Dict[str, Any]:
        """Retrieve accounts for an item."""
        if not self.is_configured():
            return {"accounts": []}
        try:
            req = AccountsGetRequest(access_token=access_token) if AccountsGetRequest else {"access_token": access_token}
            resp = self.client().accounts_get(req)
            return resp.to_dict()
        except Exception:
            logger.exception("Failed to get accounts")
            raise

    # PUBLIC_INTERFACE
    def get_transactions_sync(self, access_token: str, cursor: Optional[str] = None, count: int = 100) -> Dict[str, Any]:
        """Use transactions/sync to fetch changes since a cursor."""
        if not self.is_configured():
            # Mock shape of Plaid transactions sync
            return {"added": [], "modified": [], "removed": [], "next_cursor": cursor or "mock-cursor", "has_more": False}
        try:
            req = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor,
                count=count,
            ) if TransactionsSyncRequest else {
                "access_token": access_token, "cursor": cursor, "count": count
            }
            resp = self.client().transactions_sync(req)
            return resp.to_dict()
        except Exception:
            logger.exception("Failed to sync transactions")
            raise


# Module-level singleton
_plaid_service: Optional[PlaidService] = None

# PUBLIC_INTERFACE
def get_plaid_service() -> PlaidService:
    """Return a singleton PlaidService based on environment configuration."""
    global _plaid_service
    if _plaid_service is None:
        _plaid_service = PlaidService(PlaidSettings())
    return _plaid_service
