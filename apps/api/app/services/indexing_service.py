from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import FileChunk, UploadedFile
from app.services.embedder import Embedder
from app.services.vector_store import DEMO_RECORDS, VectorStore


class IndexingService:
    def __init__(self, db: Session, vector_store: VectorStore, embedder: Embedder):
        self.db = db
        self.vector_store = vector_store
        self.embedder = embedder

    def _chunk_records(self) -> list[dict[str, str | list[str]]]:
        stmt = (
            select(FileChunk, UploadedFile)
            .join(UploadedFile, UploadedFile.id == FileChunk.file_id)
            .where(UploadedFile.is_active.is_(True))
            .order_by(UploadedFile.id.asc(), FileChunk.chunk_index.asc())
        )

        records: list[dict[str, str | list[str]]] = []
        for chunk, file_obj in self.db.execute(stmt).all():
            records.append(
                {
                    "record_id": chunk.record_id,
                    "question": f"{file_obj.original_name} - chunk {chunk.chunk_index + 1}",
                    "answer_snippet": chunk.chunk_text,
                    "tags": ["uploaded", "admin", file_obj.original_name.lower()],
                }
            )
        return records

    def rebuild_index(self) -> int:
        records = [*DEMO_RECORDS, *self._chunk_records()]
        self.vector_store.rebuild_from_records(records=records, embedder=self.embedder)
        return len(records)
