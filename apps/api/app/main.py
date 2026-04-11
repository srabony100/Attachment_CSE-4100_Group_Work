from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes.admin import router as admin_router
from app.api.routes.auth import router as auth_router
from app.api.routes.history import router as history_router
from app.api.routes.search import router as search_router
from app.core.config import settings
from app.db.session import SessionLocal, init_db
from app.schemas.search import HealthResponse
from app.services.auth_service import AuthService
from app.services.embedder import Embedder
from app.services.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        AuthService(db).seed_admin_if_needed()
    finally:
        db.close()

    # Load reusable search resources once at startup.
    vector_store = VectorStore(
        index_path=settings.faiss_index_path,
        id_map_path=settings.id_map_path,
        lookup_map_path=settings.lookup_map_path,
    )
    startup_error: str | None = None
    try:
        vector_store.ensure_demo_index()
        vector_store.load()
    except Exception as exc:
        # Keep API process alive even when index artifacts are missing.
        startup_error = str(exc)

    embedder = Embedder(
        endpoint=settings.github_models_endpoint,
        api_key=settings.github_models_api_key,
        embedding_model=settings.embedding_model,
        timeout_seconds=settings.embedding_timeout_seconds,
        max_retries=settings.embedding_max_retries,
        base_backoff_seconds=settings.embedding_base_backoff_seconds,
    )

    app.state.vector_store = vector_store
    app.state.embedder = embedder
    app.state.startup_error = startup_error

    yield


app = FastAPI(title=settings.api_title, version=settings.api_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"error": "ValidationError", "detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "InternalServerError", "detail": "Unexpected server error"})


@app.get("/health", tags=["health"])
def health(request: Request) -> HealthResponse:
    vector_store: VectorStore | None = getattr(request.app.state, "vector_store", None)
    startup_error: str | None = getattr(request.app.state, "startup_error", None)
    loaded = bool(vector_store and vector_store.is_ready)
    index_size = int(vector_store.index.ntotal) if vector_store and vector_store.index else 0

    return HealthResponse(
        status="ok" if loaded else "degraded",
        index_loaded=loaded,
        index_size=index_size,
        embedding_model=settings.embedding_model,
        startup_error=startup_error,
    )


app.include_router(search_router)
app.include_router(auth_router)
app.include_router(history_router)
app.include_router(admin_router)
