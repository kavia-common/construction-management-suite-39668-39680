from typing import Optional

from src.core.config import settings

try:
    from supabase import create_client, Client  # type: ignore
except Exception:
    # supabase-py may not be installed in some environments; define a shim type.
    Client = object  # type: ignore
    create_client = None  # type: ignore

_supabase_client: Optional["Client"] = None


def get_supabase_client() -> Optional["Client"]:
    """
    Get or initialize the Supabase client using environment variables.

    Returns:
        A Supabase Client instance if SUPABASE_URL and SUPABASE_ANON_KEY are set
        and the supabase package is available; otherwise None.
    """
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client

    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        return None

    if create_client is None:
        # supabase library is not installed
        return None

    _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    return _supabase_client
