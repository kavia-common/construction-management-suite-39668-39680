# Construction Management Suite - Backend API

FastAPI backend providing RESTful endpoints for authentication, projects, estimates, jobs, proposals, invoices, receipts, contracts, marketing, reports, and integrations.

## Run

1. Create a virtual environment and install dependencies:
   - pip install -r requirements.txt

2. Configure environment variables:
   - Copy `.env.example` to `.env` and set values appropriately (Supabase and database).

3. Start the server:
   - uvicorn src.api.main:app --reload --port 3001

Open docs at http://localhost:3001/docs (Ocean Professional themed Swagger UI).

## Supabase

- Set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env` to enable authentication endpoints.
- Frontend should set emailRedirectTo using the SITE_URL environment for signup flows.

## Database

- This codebase honors dependency on `construction_management_db`.
- Provide the connection details via the documented env vars; integrate an ORM/driver (e.g., SQLAlchemy/psycopg/asyncpg) inside `src/core/db.py` as needed.
