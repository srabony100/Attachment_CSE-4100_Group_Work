from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.core.config import settings
from app.db.session import get_db
from app.models.entities import User
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import AuthError, AuthService
from app.services.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookies(response: Response, token: str, role: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="user_role",
        value=role,
        httponly=False,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("user_role", path="/")


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.register_user(payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    token = create_access_token(subject=str(user.id), role=user.role)
    _set_auth_cookies(response, token, user.role)

    return AuthResponse(
        message="Registration successful",
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password, required_role="user")
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    token = create_access_token(subject=str(user.id), role=user.role)
    _set_auth_cookies(response, token, user.role)

    return AuthResponse(
        message="Login successful",
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        ),
    )


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    _clear_auth_cookies(response)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_active_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        status=current_user.status,
        created_at=current_user.created_at,
    )
