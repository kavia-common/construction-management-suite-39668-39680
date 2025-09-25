import os
from functools import lru_cache
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    APP_NAME: str = Field(default="Construction Management Suite - Backend API", description="Application name.")
    ENV: str = Field(default=os.getenv("ENV", "development"), description="Runtime environment.")
    CORS_ALLOW_ORIGINS: str = Field(default=os.getenv("CORS_ALLOW_ORIGINS", "*"), description="Comma-separated CORS origins.")

    # Supabase integration
    SUPABASE_URL: str = Field(default=os.getenv("SUPABASE_URL", ""), description="Supabase project URL.")
    SUPABASE_ANON_KEY: str = Field(default=os.getenv("SUPABASE_ANON_KEY", ""), description="Supabase anon/public key for client operations.")

    # Database dependency (construction_management_db)
    # Use provided env var names from dependency container; do not assume contents.
    DB_URL: str = Field(default=os.getenv("CONSTRUCTION_DB_URL", ""), description="Database URL for construction_management_db or equivalent.")
    DB_USER: str = Field(default=os.getenv("CONSTRUCTION_DB_USER", ""), description="Database user.")
    DB_PASSWORD: str = Field(default=os.getenv("CONSTRUCTION_DB_PASSWORD", ""), description="Database password.")
    DB_NAME: str = Field(default=os.getenv("CONSTRUCTION_DB_NAME", ""), description="Database name.")
    DB_PORT: str = Field(default=os.getenv("CONSTRUCTION_DB_PORT", ""), description="Database port.")
    DB_DRIVER: str = Field(default=os.getenv("CONSTRUCTION_DB_DRIVER", "postgresql"), description="DB driver (e.g., postgresql, mysql).")


@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()


# singleton settings
settings = get_settings()
