from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status

from .config import get_settings


@dataclass
class AuthContext:
    user_id: str
    roles: set[str]
    scopes: set[str]


def _parse_token(token: str | None) -> AuthContext:
    if not token:
        return AuthContext(user_id="anonymous", roles={"viewer"}, scopes={"read"})
    parts = token.replace("Bearer", "").strip().split(";")
    parsed = {"user": "anonymous", "roles": "viewer", "scopes": "read"}
    for part in parts:
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key.strip()] = value.strip()
    return AuthContext(
        user_id=parsed["user"],
        roles={r for r in parsed["roles"].split(",") if r},
        scopes={s for s in parsed["scopes"].split(",") if s},
    )


def get_auth_context(authorization: str | None = Header(default=None)) -> AuthContext:
    settings = get_settings()
    if settings.require_auth and not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing authorization")
    return _parse_token(authorization)


def require_scope(scope: str):
    def dependency(ctx: AuthContext = Depends(get_auth_context)) -> AuthContext:
        if scope not in ctx.scopes and "admin" not in ctx.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"missing scope: {scope}")
        return ctx

    return dependency
