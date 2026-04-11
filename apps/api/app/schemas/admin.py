from datetime import datetime

from pydantic import BaseModel


class UserAdminItem(BaseModel):
    id: int
    email: str
    role: str
    status: str
    created_at: datetime


class UserAdminListResponse(BaseModel):
    users: list[UserAdminItem]


class UploadedFileItem(BaseModel):
    id: int
    original_name: str
    mime_type: str
    size_bytes: int
    chunk_count: int
    uploader_id: int
    uploaded_at: datetime


class UploadedFileListResponse(BaseModel):
    files: list[UploadedFileItem]


class FileChunkPreviewItem(BaseModel):
    id: int
    chunk_index: int
    preview_text: str


class FileChunkPreviewResponse(BaseModel):
    file_id: int
    chunks: list[FileChunkPreviewItem]


class AdminLogItem(BaseModel):
    id: int
    admin_user_id: int
    action_type: str
    target_entity_type: str
    target_entity_id: str | None
    description: str
    created_at: datetime


class AdminLogListResponse(BaseModel):
    logs: list[AdminLogItem]


class DashboardAnalyticsResponse(BaseModel):
    total_users: int
    active_users: int
    blocked_users: int
    total_uploaded_files: int
    total_indexed_chunks: int
    total_searches: int
    recent_admin_activities: int
    recent_uploads: int
