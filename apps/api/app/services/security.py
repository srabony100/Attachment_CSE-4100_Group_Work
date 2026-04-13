from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


class TokenError(ValueError):
    pass


def hash_password(password: str) -> str:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        # bcrypt has a 72-byte input limit.
        raise ValueError("Password is too long")
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    raw = password.encode("utf-8")
    if len(raw) > 72:
        return False
    return bcrypt.checkpw(raw, password_hash.encode("utf-8"))


def create_access_token(subject: str, role: str) -> str:
    expire_at = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": subject,
        "role": role,
        "exp": expire_at,
        "iss": settings.jwt_issuer,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=settings.jwt_issuer,
        )
    except JWTError as exc:
        raise TokenError("Invalid or expired token") from exc

    subject = payload.get("sub")
    role = payload.get("role")
    if not subject or not role:
        raise TokenError("Token payload is missing required claims")

    return {"sub": str(subject), "role": str(role)}
