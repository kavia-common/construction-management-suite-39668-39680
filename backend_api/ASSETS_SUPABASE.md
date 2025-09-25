# Supabase Integration (Backend API)

The backend integrates with Supabase authentication using supabase-py.

Environment variables (required):
- SUPABASE_URL
- SUPABASE_ANON_KEY

Optional app variables:
- CORS_ALLOW_ORIGINS (default "*")

Where it is used:
- src/core/supabase_client.py initializes a singleton Supabase client if env is present.
- src/routers/auth.py exposes signup/signin/signout endpoints that proxy to Supabase when configured.

Quickstart
1) Create .env in backend_api with:
   SUPABASE_URL=your-project-url
   SUPABASE_ANON_KEY=your-anon-key
   CORS_ALLOW_ORIGINS=http://localhost:3000

2) Install and run:
   pip install -r requirements.txt
   uvicorn src.api.main:app --reload --port 3001

3) Test:
   curl -X POST http://localhost:3001/auth/signup -H "Content-Type: application/json" -d '{
     "email": "test@example.com",
     "password": "secret12",
     "redirect_to": "http://localhost:3000/auth/callback"
   }'

Database and RLS
- Supabase tables configured by this setup: profiles, projects, estimates
- RLS ensures users only access rows where owner_id = auth.uid() (for projects, estimates) or their own profile row.

Security Notes
- Never commit keys.
- For server-to-server operations, use the service role key in your deployment environment (do not place it in client code).
