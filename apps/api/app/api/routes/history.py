from __future__ import annotations

from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_active_user
from app.models.entities import User
from app.schemas.history import SearchHistoryItem, SearchHistoryResponse
from app.services.history_service import HistoryService
from app.db.session import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=SearchHistoryResponse)
def user_history(
    limit: int = 25,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SearchHistoryResponse:
    items = HistoryService(db).list_user_history(user_id=current_user.id, limit=min(max(limit, 1), 100))
    return SearchHistoryResponse(
        items=[
            SearchHistoryItem(
                id=item.id,
                query_text=item.query_text,
                result_record_id=item.result_record_id,
                result_title=item.result_title,
                created_at=item.created_at,
            )
            for item in items
        ]
    )
