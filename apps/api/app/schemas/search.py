from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=3)
    top_k: int = Field(default=10, ge=1, le=50)
    tags: list[str] = Field(default_factory=list)


class SearchResultItem(BaseModel):
    record_id: str
    title: str
    answer_snippet: str
    tags: list[str]
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]


class HealthResponse(BaseModel):
    status: str
    index_loaded: bool
    index_size: int
    embedding_model: str
    startup_error: str | None = None
