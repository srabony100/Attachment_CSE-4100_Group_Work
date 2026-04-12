from datetime import datetime

from pydantic import BaseModel


class SearchHistoryItem(BaseModel):
    id: int
    query_text: str
    result_record_id: str | None
    result_title: str | None
    created_at: datetime


class SearchHistoryResponse(BaseModel):
    items: list[SearchHistoryItem]
