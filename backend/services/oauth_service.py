"""
OAuth/OIDC helpers that are independent of FastAPI and Authlib.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class OAuthProfile:
    provider: str
    subject: str
    email: str | None
    email_verified: bool | None
    display_name: str | None
    username_seed: str


def normalize_oidc_userinfo(provider: str, userinfo: dict[str, Any]) -> OAuthProfile:
    """Normalize provider claims into the stable identity persisted by LitMatch."""
    subject = str(userinfo.get("sub") or "").strip()
    if not subject:
        raise ValueError("OIDC userinfo is missing required subject claim.")

    raw_email = userinfo.get("email")
    email = str(raw_email).strip().lower() if raw_email else None
    display_name = str(
        userinfo.get("name") or userinfo.get("preferred_username") or ""
    ).strip() or None
    email_verified = userinfo.get("email_verified")
    if email_verified is not None:
        email_verified = bool(email_verified)

    seed_source = email.split("@", 1)[0] if email else display_name
    username_seed = _username_seed(seed_source or f"{provider}_{subject}")

    return OAuthProfile(
        provider=provider,
        subject=subject,
        email=email,
        email_verified=email_verified,
        display_name=display_name,
        username_seed=username_seed,
    )


def safe_post_login_redirect(
    candidate: str | None,
    default: str,
    allowed_origins: list[str],
) -> str:
    """
    Return a post-login redirect target without allowing open redirects.

    Relative paths are anchored to the default frontend origin. Absolute URLs
    must match one of the configured origins exactly.
    """
    if not candidate:
        return default

    candidate = candidate.strip()
    if not candidate or candidate.startswith("//"):
        return default

    default_parts = urlparse(default)
    default_origin = _origin(default_parts)

    if candidate.startswith("/"):
        return f"{default_origin}{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme and parsed.netloc:
        allowed = {_origin(urlparse(origin)) for origin in allowed_origins}
        if _origin(parsed) in allowed:
            return candidate

    return default


def _origin(parsed) -> str:
    return f"{parsed.scheme}://{parsed.netloc}"


def _username_seed(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip().lower())
    normalized = re.sub(r"-{2,}", "-", normalized).strip("-_")
    return (normalized or "oauth-user")[:40]
