from fastapi import APIRouter, Depends, HTTPException, Request

from sqlalchemy.orm import Session

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.search import SearchRequest, SearchResponse
from app.services.embedder import Embedder
from app.services.history_service import HistoryService
from app.services.search_service import SearchService
from app.services.vector_store import VectorStore

router = APIRouter(tags=["search"])


def _get_services(request: Request) -> tuple[Embedder, VectorStore]:
    embedder: Embedder | None = getattr(request.app.state, "embedder", None)
    vector_store: VectorStore | None = getattr(request.app.state, "vector_store", None)

    if embedder is None or vector_store is None or not vector_store.is_ready:
        raise HTTPException(status_code=503, detail="Search service is not ready")

    return embedder, vector_store


@router.post("/search", response_model=SearchResponse)
@router.post("/api/v1/search", response_model=SearchResponse)
def semantic_search(
    payload: SearchRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> SearchResponse:
    embedder, vector_store = _get_services(request)
    search_service = SearchService(embedder, vector_store, HistoryService(db))

    try:
        return search_service.run_search(payload=payload, user=current_user)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Search failed") from exc
