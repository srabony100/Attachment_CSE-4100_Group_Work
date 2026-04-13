from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import User
from app.services.security import hash_password, verify_password


class AuthError(ValueError):
    pass


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self.db.scalar(stmt)

    def get_by_id(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def register_user(self, email: str, password: str) -> User:
        normalized = email.lower().strip()
        if self.get_by_email(normalized):
            raise AuthError("Email is already registered")

        try:
            password_hash = hash_password(password)
        except ValueError as exc:
            raise AuthError("Password is too long") from exc

        user = User(
            email=normalized,
            password_hash=password_hash,
            role="user",
            status="active",
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str, required_role: str | None = None) -> User:
        user = self.get_by_email(email)
        if user is None or not verify_password(password, user.password_hash):
            raise AuthError("Invalid credentials")
        if user.status != "active":
            raise AuthError("This account is blocked")
        if required_role and user.role != required_role:
            raise AuthError("Access denied")
        return user

    def seed_admin_if_needed(self) -> User | None:
        if not settings.seed_admin_email or not settings.seed_admin_password:
            return None

        existing = self.get_by_email(settings.seed_admin_email)
        if existing is not None:
            if existing.role != "admin":
                existing.role = "admin"
                existing.status = "active"
                self.db.add(existing)
                self.db.commit()
                self.db.refresh(existing)
            return existing

        admin = User(
            email=settings.seed_admin_email.lower().strip(),
            password_hash=hash_password(settings.seed_admin_password),
            role="admin",
            status="active",
        )
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        return admin
