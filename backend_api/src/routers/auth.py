from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

from src.core.supabase_client import get_supabase_client

router = APIRouter()


class SignupRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=6, description="Password (min 6 chars)")
    redirect_to: Optional[str] = Field(None, description="Redirect URL for email confirmation (use SITE_URL env in frontend).")


class AuthResponse(BaseModel):
    message: str = Field(..., description="Status message.")


# PUBLIC_INTERFACE
@router.post("/signup", summary="Sign up with Supabase", description="Create a new user using Supabase auth.", response_model=AuthResponse)
def signup(req: SignupRequest):
    """This is a public function."""
    sb = get_supabase_client()
    if sb is None:
        # In local scaffolding, Supabase may be absent; return mocked response.
        return AuthResponse(message="Supabase not configured; user signup request received.")
    try:
        auth = sb.auth.sign_up({"email": str(req.email), "password": req.password, "options": {"emailRedirectTo": req.redirect_to}})
        if auth and getattr(auth, "user", None):
            return AuthResponse(message="User created.")
        return AuthResponse(message="Signup initiated.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Signup failed: {ex}")


class SigninRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="Password")


class SigninResponse(BaseModel):
    access_token: Optional[str] = Field(None, description="Access token if authentication succeeded.")
    message: str = Field(..., description="Status message.")


# PUBLIC_INTERFACE
@router.post("/signin", summary="Sign in with Supabase", description="Authenticate a user using Supabase auth.", response_model=SigninResponse)
def signin(req: SigninRequest):
    """This is a public function."""
    sb = get_supabase_client()
    if sb is None:
        return SigninResponse(message="Supabase not configured; mock sign-in success.", access_token=None)
    try:
        res = sb.auth.sign_in_with_password({"email": str(req.email), "password": req.password})
        access_token = None
        if res and getattr(res, "session", None) and getattr(res.session, "access_token", None):
            access_token = res.session.access_token
        return SigninResponse(message="Sign-in processed.", access_token=access_token)
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Sign-in failed: {ex}")


# PUBLIC_INTERFACE
@router.post("/signout", summary="Sign out", description="Sign out the current user.", response_model=AuthResponse)
def signout():
    """This is a public function."""
    sb = get_supabase_client()
    if sb is None:
        return AuthResponse(message="Supabase not configured; mock sign-out success.")
    try:
        sb.auth.sign_out()
        return AuthResponse(message="Signed out.")
    except Exception as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Sign-out failed: {ex}")
