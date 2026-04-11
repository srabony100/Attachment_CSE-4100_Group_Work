from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


API_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
DATA_INDEX_DIR = REPO_ROOT / "data" / "index"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(API_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api_title: str = "Semantic Programming Search API"
    api_version: str = "0.1.0"

    github_models_api_key: str = ""
    github_models_endpoint: str = "https://models.inference.ai.azure.com/embeddings"
    embedding_model: str = "text-embedding-3-large"
    embedding_timeout_seconds: float = 45.0
    embedding_max_retries: int = 5
    embedding_base_backoff_seconds: float = 1.0

    faiss_index_path: str = str(DATA_INDEX_DIR / "question_index.faiss")
    id_map_path: str = str(DATA_INDEX_DIR / "id_map.npy")
    lookup_map_path: str = str(DATA_INDEX_DIR / "record_lookup.json")
    default_top_k: int = 10
    database_url: str = f"sqlite:///{REPO_ROOT / 'data' / 'app.db'}"
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "semantic-search-api"
    jwt_access_token_expire_minutes: int = 60 * 12
    cookie_secure: bool = False

    seed_admin_email: str = ""
    seed_admin_password: str = ""

    upload_dir: str = str(API_ROOT.parent / "uploads")
    max_upload_size_bytes: int = 5 * 1024 * 1024

    cors_origins: str = (
        "http://localhost:3000,"
        "http://127.0.0.1:3000,"
        "http://localhost:3001,"
        "http://127.0.0.1:3001"
    )
    cors_origin_regex: str = r"^https?://(localhost|127\.0\.0\.1)(:\\d+)?$"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
