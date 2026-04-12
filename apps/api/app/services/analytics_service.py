from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import AdminActivityLog, FileChunk, SearchHistory, UploadedFile, User


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def dashboard_metrics(self) -> dict[str, int]:
        now = datetime.now(timezone.utc)
        last_7_days = now - timedelta(days=7)

        total_users = self.db.scalar(select(func.count(User.id))) or 0
        active_users = self.db.scalar(select(func.count(User.id)).where(User.status == "active")) or 0
        blocked_users = self.db.scalar(select(func.count(User.id)).where(User.status == "blocked")) or 0
        total_uploaded_files = self.db.scalar(
            select(func.count(UploadedFile.id)).where(UploadedFile.is_active.is_(True))
        ) or 0
        total_indexed_chunks = self.db.scalar(select(func.count(FileChunk.id))) or 0
        total_searches = self.db.scalar(select(func.count(SearchHistory.id))) or 0
        recent_admin_activities = self.db.scalar(
            select(func.count(AdminActivityLog.id)).where(AdminActivityLog.created_at >= last_7_days)
        ) or 0
        recent_uploads = self.db.scalar(
            select(func.count(UploadedFile.id)).where(UploadedFile.uploaded_at >= last_7_days)
        ) or 0

        return {
            "total_users": int(total_users),
            "active_users": int(active_users),
            "blocked_users": int(blocked_users),
            "total_uploaded_files": int(total_uploaded_files),
            "total_indexed_chunks": int(total_indexed_chunks),
            "total_searches": int(total_searches),
            "recent_admin_activities": int(recent_admin_activities),
            "recent_uploads": int(recent_uploads),
        }
