from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import User


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def list_users(self) -> list[User]:
        stmt = select(User).order_by(User.created_at.desc())
        return list(self.db.scalars(stmt).all())

    def get_user(self, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        return self.db.scalar(stmt)

    def update_status(self, user_id: int, status: str) -> User:
        user = self.get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        user.status = status
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
