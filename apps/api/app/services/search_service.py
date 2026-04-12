from __future__ import annotations

from app.models.entities import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedder import Embedder
from app.services.history_service import HistoryService
from app.services.vector_store import VectorStore


class SearchService:
    def __init__(self, embedder: Embedder, vector_store: VectorStore, history_service: HistoryService):
        self.embedder = embedder
        self.vector_store = vector_store
        self.history_service = history_service

    def run_search(self, payload: SearchRequest, user: User) -> SearchResponse:
        vector = self.embedder.embed(payload.query)
        results = self.vector_store.search(
            query_vector=vector,
            top_k=payload.top_k,
            tags=payload.tags,
        )

        top = results[0] if results else None
        try:
            self.history_service.add_entry(
                user_id=user.id,
                query_text=payload.query,
                result_record_id=top.record_id if top else None,
                result_title=top.title if top else None,
            )
        except Exception:
            # Search responses should still succeed even if history storage is temporarily unavailable.
            pass

        return SearchResponse(query=payload.query, results=results)
