import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

# Load environment variables at app start
load_dotenv()

# Local imports for routers and core modules
from src.core.config import settings
from src.core.supabase_client import get_supabase_client
from src.core.db import get_db_connection
from src.routers import (
    auth,
    projects,
    estimates,
    jobs,
    proposals,
    invoices,
    receipts,
    contracts,
    marketing,
    reports,
    integrations,
)

# Define OpenAPI tags for grouping
openapi_tags = [
    {"name": "Health", "description": "Service health and metadata."},
    {"name": "Auth", "description": "Authentication and user management."},
    {"name": "Projects", "description": "Project management APIs."},
    {"name": "Estimates", "description": "Estimating workflows and items."},
    {"name": "Jobs", "description": "Job tracking and assignments."},
    {"name": "Proposals", "description": "Proposals and approvals."},
    {"name": "Invoices", "description": "Invoicing and payments."},
    {"name": "Receipts", "description": "Receipt tracking."},
    {"name": "Contracts", "description": "Contract management and signatures."},
    {"name": "Marketing", "description": "Leads, campaigns, and outreach."},
    {"name": "Reports", "description": "Reporting and analytics."},
    {"name": "Integrations", "description": "3rd-party integrations & webhooks."},
]

description = (
    "Construction Management Suite API. A comprehensive backend for remodeling "
    "business operations including authentication, estimation, project tracking, "
    "contracts, invoicing, marketing, backlog management, and reporting.\n\n"
    "Ocean Professional Theme: Blue & amber accents; modern, clean UI in docs."
)

app = FastAPI(
    title="Construction Management Suite - Backend API",
    description=description,
    version="1.0.0",
    terms_of_service="https://example.com/terms",
    contact={
        "name": "Support",
        "url": "https://example.com/support",
        "email": "support@example.com",
    },
    license_info={
        "name": "Proprietary",
        "url": "https://example.com/license",
    },
    openapi_tags=openapi_tags,
)

# CORS configuration (allow configurable origins)
allow_origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_INTERFACE
@app.get("/", tags=["Health"], summary="Health Check", description="Simple health check endpoint to verify service availability.", response_model=dict)
def health_check():
    """This is a public function."""
    return {"message": "Healthy"}

# PUBLIC_INTERFACE
@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    """Serve Swagger UI with Ocean Professional theme colors."""
    swagger_ui_parameters = {
        "defaultModelsExpandDepth": -1,
        "docExpansion": "none",
        "displayRequestDuration": True,
    }
    html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="Construction Management Suite - Docs",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_ui_parameters=swagger_ui_parameters,
    )
    # Inject custom CSS for Ocean Professional theme (blue/amber)
    custom_css = """
    <style>
      :root {
        --primary: #2563EB;
        --secondary: #F59E0B;
        --background: #f9fafb;
        --surface: #ffffff;
        --text: #111827;
      }
      body { background: var(--background); }
      .swagger-ui .topbar { background: linear-gradient(90deg, #2563EB, #1E40AF); }
      .swagger-ui .topbar a span { color: #fff !important; }
      .swagger-ui .opblock-summary-method,
      .swagger-ui .btn.try-out__btn,
      .swagger-ui .btn.execute.opblock-control__btn {
        background: var(--primary) !important;
        border-color: var(--primary) !important;
      }
      .swagger-ui .btn.try-out__btn:hover,
      .swagger-ui .btn.execute.opblock-control__btn:hover {
        background: #1D4ED8 !important;
      }
      .swagger-ui .opblock .opblock-summary-description { color: var(--text); }
      .swagger-ui .model-box { box-shadow: 0 1px 3px rgba(0,0,0,0.06); border-radius: 8px; }
      .swagger-ui .scheme-container { background: var(--surface); border-radius: 8px; }
      .swagger-ui .info .title { color: var(--text); }
      .swagger-ui .info .base-url { color: var(--secondary); }
    </style>
    """
    return HTMLResponse(content=html.body.decode() + custom_css, status_code=200)

# PUBLIC_INTERFACE
@app.get("/docs/oauth2-redirect", include_in_schema=False)
def swagger_ui_redirect():
    """OAuth2 redirect HTML for Swagger UI."""
    return HTMLResponse(get_swagger_ui_oauth2_redirect_html())

# PUBLIC_INTERFACE
@app.get("/websocket-usage", tags=["Health"], summary="WebSocket Usage", description="This API currently does not expose public WebSocket endpoints. Future real-time updates will be documented here.", response_model=dict)
def websocket_usage():
    """This is a public function."""
    return {"websocket": "No public websocket endpoints available yet."}

# Register routers with tags
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(estimates.router, prefix="/estimates", tags=["Estimates"])
app.include_router(jobs.router, prefix="/jobs", tags=["Jobs"])
app.include_router(proposals.router, prefix="/proposals", tags=["Proposals"])
app.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])
app.include_router(receipts.router, prefix="/receipts", tags=["Receipts"])
app.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
app.include_router(marketing.router, prefix="/marketing", tags=["Marketing"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])
app.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])

# Startup checks
@app.on_event("startup")
async def on_startup():
    # Ensure Supabase URL and Key are set when using Supabase
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY:
        _ = get_supabase_client()
    # Test DB connection if env configured
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
    except Exception:
        # DB might not be configured during initial scaffolding; ignore to allow app start.
        pass
