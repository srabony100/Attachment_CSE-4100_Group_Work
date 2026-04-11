from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import uuid4

from docx import Document
from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import FileChunk, UploadedFile, User

ALLOWED_EXTENSIONS = {".txt", ".md", ".json", ".pdf", ".docx"}


class FileService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def _sanitize_filename(self, filename: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
        return safe[:180] if safe else "upload"

    def _validate_upload(self, file: UploadFile, size_bytes: int) -> None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {suffix or 'unknown'}")
        if size_bytes > settings.max_upload_size_bytes:
            raise ValueError(f"File is too large. Max size is {settings.max_upload_size_bytes} bytes")

    def _extract_text(self, target_path: Path) -> str:
        suffix = target_path.suffix.lower()
        if suffix in {".txt", ".md"}:
            return target_path.read_text(encoding="utf-8", errors="ignore")
        if suffix == ".json":
            payload = json.loads(target_path.read_text(encoding="utf-8", errors="ignore"))
            return json.dumps(payload, ensure_ascii=True, indent=2)
        if suffix == ".pdf":
            reader = PdfReader(str(target_path))
            pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(pages)
        if suffix == ".docx":
            document = Document(str(target_path))
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        raise ValueError("Unsupported file type")

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 750, overlap: int = 120) -> list[str]:
        normalized = re.sub(r"\s+", " ", text).strip()
        if not normalized:
            return []

        chunks: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(len(normalized), start + chunk_size)
            chunk = normalized[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(normalized):
                break
            start = max(end - overlap, start + 1)
        return chunks

    def save_upload(self, file: UploadFile, admin_user: User) -> UploadedFile:
        raw = file.file.read()
        size_bytes = len(raw)
        self._validate_upload(file, size_bytes)

        original_name = file.filename or "upload"
        safe_name = self._sanitize_filename(original_name)
        stored_name = f"{uuid4().hex}_{safe_name}"
        target_path = self.upload_dir / stored_name
        target_path.write_bytes(raw)

        extracted_text = self._extract_text(target_path)
        chunks = self._chunk_text(extracted_text)
        if not chunks:
            target_path.unlink(missing_ok=True)
            raise ValueError("No indexable text could be extracted from file")

        upload = UploadedFile(
            original_name=original_name,
            stored_name=stored_name,
            stored_path=str(target_path),
            mime_type=file.content_type or "application/octet-stream",
            size_bytes=size_bytes,
            uploader_id=admin_user.id,
            is_active=True,
        )
        self.db.add(upload)
        self.db.commit()
        self.db.refresh(upload)

        file_chunks: list[FileChunk] = []
        for idx, chunk_text in enumerate(chunks):
            file_chunks.append(
                FileChunk(
                    file_id=upload.id,
                    chunk_index=idx,
                    record_id=f"upload-{upload.id}-chunk-{idx}",
                    chunk_text=chunk_text,
                )
            )

        self.db.add_all(file_chunks)
        self.db.commit()
        return upload

    def list_files(self) -> list[tuple[UploadedFile, int]]:
        stmt = (
            select(UploadedFile, func.count(FileChunk.id))
            .join(FileChunk, FileChunk.file_id == UploadedFile.id, isouter=True)
            .where(UploadedFile.is_active.is_(True))
            .group_by(UploadedFile.id)
            .order_by(UploadedFile.uploaded_at.desc())
        )
        return list(self.db.execute(stmt).all())

    def delete_file(self, file_id: int) -> UploadedFile:
        file_obj = self.db.get(UploadedFile, file_id)
        if file_obj is None or not file_obj.is_active:
            raise ValueError("File not found")

        file_obj.is_active = False
        target_path = Path(file_obj.stored_path)
        target_path.unlink(missing_ok=True)
        self.db.add(file_obj)
        self.db.commit()
        self.db.refresh(file_obj)

        stmt = select(FileChunk).where(FileChunk.file_id == file_id)
        chunks = self.db.scalars(stmt).all()
        for chunk in chunks:
            self.db.delete(chunk)
        self.db.commit()

        return file_obj

    def get_chunks_for_file(self, file_id: int, limit: int = 20) -> list[FileChunk]:
        file_obj = self.db.get(UploadedFile, file_id)
        if file_obj is None or not file_obj.is_active:
            raise ValueError("File not found")
        stmt = (
            select(FileChunk)
            .where(FileChunk.file_id == file_id)
            .order_by(FileChunk.chunk_index.asc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())
