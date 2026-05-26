"""
OAuth login, callback, session introspection, and logout endpoints.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_db
from core.config import settings
from models.schemas import UserResponse
from services import db_postgres as db
from services.oauth_service import normalize_oidc_userinfo, safe_post_login_redirect

try:
    from authlib.integrations.base_client import OAuthError
    from authlib.integrations.starlette_client import OAuth
except ImportError:  # pragma: no cover - exercised only when deps are missing.
    OAuth = None

    class OAuthError(Exception):
        pass


router = APIRouter(prefix="/auth", tags=["auth"])

SUPPORTED_PROVIDERS = {"google"}
SESSION_USER_ID_KEY = "user_id"
SESSION_PROVIDER_KEY = "auth_provider"
SESSION_NEXT_KEY = "oauth_next"

_oauth_registry = None


def get_oauth_client(provider: str):
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unsupported OAuth provider.",
        )
    if OAuth is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth dependencies are not installed.",
        )
    if not settings.SESSION_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Session secret key is not configured.",
        )
    if not settings.OAUTH_GOOGLE_CLIENT_ID or not settings.OAUTH_GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth provider is not configured.",
        )

    registry = _get_oauth_registry()
    client = registry.create_client(provider)
    if client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OAuth provider is not configured.",
        )
    return client


@router.get("/login/{provider}")
async def oauth_login(
    provider: str,
    request: Request,
    next: str | None = None,
    oauth_client=Depends(get_oauth_client),
):
    request.session[SESSION_NEXT_KEY] = safe_post_login_redirect(
        next,
        settings.OAUTH_POST_LOGIN_REDIRECT,
        settings.OAUTH_ALLOWED_REDIRECT_ORIGINS,
    )
    redirect_uri = _callback_redirect_uri(request, provider)
    return await oauth_client.authorize_redirect(request, redirect_uri)


@router.get("/callback/{provider}")
async def oauth_callback(
    provider: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    oauth_client=Depends(get_oauth_client),
):
    try:
        token = await oauth_client.authorize_access_token(request)
    except OAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth callback validation failed.",
        ) from exc

    userinfo = token.get("userinfo")
    if not userinfo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OAuth provider did not return user information.",
        )

    try:
        profile = normalize_oidc_userinfo(provider, dict(userinfo))
        user = await db.upsert_oauth_user(session, profile)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    request.session[SESSION_USER_ID_KEY] = str(user.id)
    request.session[SESSION_PROVIDER_KEY] = provider
    redirect_to = request.session.pop(
        SESSION_NEXT_KEY,
        settings.OAUTH_POST_LOGIN_REDIRECT,
    )
    return RedirectResponse(redirect_to, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/me", response_model=UserResponse)
async def get_current_session_user(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    user_id = _session_user_id(request)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    user = await db.get_user(session, user_id)
    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    response = JSONResponse({"ok": True})
    response.delete_cookie(
        settings.SESSION_COOKIE_NAME,
        path="/",
    )
    return response


def _get_oauth_registry():
    global _oauth_registry
    if _oauth_registry is None:
        registry = OAuth()
        registry.register(
            name="google",
            client_id=settings.OAUTH_GOOGLE_CLIENT_ID,
            client_secret=settings.OAUTH_GOOGLE_CLIENT_SECRET,
            server_metadata_url=settings.OAUTH_GOOGLE_SERVER_METADATA_URL,
            client_kwargs={
                "scope": settings.OAUTH_GOOGLE_SCOPE,
                "code_challenge_method": "S256",
            },
        )
        _oauth_registry = registry
    return _oauth_registry


def _callback_redirect_uri(request: Request, provider: str) -> str:
    base_url = settings.OAUTH_CALLBACK_BASE_URL.strip().rstrip("/")
    if base_url:
        return f"{base_url}/api/v1/auth/callback/{provider}"
    return str(request.url_for("oauth_callback", provider=provider))


def _session_user_id(request: Request) -> UUID | None:
    value = request.session.get(SESSION_USER_ID_KEY)
    if not value:
        return None
    try:
        return UUID(str(value))
    except ValueError:
        request.session.clear()
        return None
