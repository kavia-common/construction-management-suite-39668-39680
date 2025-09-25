from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class Pagination(BaseModel):
    """Pagination parameters for listing endpoints."""
    page: int = Field(1, description="Page number, starting from 1.")
    page_size: int = Field(20, description="Number of items per page.")


class PaginatedResponse(BaseModel):
    """Generic paginated response envelope."""
    total: int = Field(..., description="Total items available.")
    page: int = Field(..., description="Current page number.")
    page_size: int = Field(..., description="Page size used.")
    items: list = Field(default_factory=list, description="List of items for the current page.")


class User(BaseModel):
    """Basic user model."""
    id: str = Field(..., description="User ID.")
    email: EmailStr = Field(..., description="Email address.")
    full_name: Optional[str] = Field(None, description="Full name.")
    is_active: bool = Field(True, description="Is the user active?")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp.")
