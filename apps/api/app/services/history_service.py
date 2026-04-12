from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import SearchHistory


class HistoryService:
    def __init__(self, db: Session):
        self.db = db

    def add_entry(
        self,
        *,
        user_id: int,
        query_text: str,
        result_record_id: str | None,
        result_title: str | None,
    ) -> SearchHistory:
        entry = SearchHistory(
            user_id=user_id,
            query_text=query_text,
            result_record_id=result_record_id,
            result_title=result_title,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def list_user_history(self, user_id: int, limit: int = 25) -> list[SearchHistory]:
        stmt = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
