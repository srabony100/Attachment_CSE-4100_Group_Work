from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_admin_user
from app.db.session import get_db
from app.models.entities import AdminActivityLog, User
from app.schemas.admin import (
    AdminLogItem,
    AdminLogListResponse,
    DashboardAnalyticsResponse,
    FileChunkPreviewItem,
    FileChunkPreviewResponse,
    UploadedFileItem,
    UploadedFileListResponse,
    UserAdminItem,
    UserAdminListResponse,
)
from app.schemas.auth import AuthResponse, LoginRequest, UserResponse
from app.services.activity_log_service import ActivityLogService
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthError, AuthService
from app.services.file_service import FileService
from app.services.indexing_service import IndexingService
from app.services.user_service import UserService
from app.services.security import create_access_token
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["admin"])


def _set_auth_cookies(response, token: str, role: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )
    response.set_cookie(
        key="user_role",
        value=role,
        httponly=False,
        samesite="lax",
        secure=settings.cookie_secure,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
    )


@router.post("/login", response_model=AuthResponse)
def admin_login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)) -> AuthResponse:
    service = AuthService(db)
    try:
        user = service.authenticate(payload.email, payload.password, required_role="admin")
    except AuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc

    token = create_access_token(subject=str(user.id), role=user.role)
    _set_auth_cookies(response, token, user.role)

    ActivityLogService(db).log(
        admin_user_id=user.id,
        action_type="admin_login",
        target_entity_type="session",
        target_entity_id=None,
        description="Admin logged in",
    )

    return AuthResponse(
        message="Admin login successful",
        user=UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            status=user.status,
            created_at=user.created_at,
        ),
    )


@router.get("/dashboard/analytics", response_model=DashboardAnalyticsResponse)
def analytics(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> DashboardAnalyticsResponse:
    metrics = AnalyticsService(db).dashboard_metrics()
    return DashboardAnalyticsResponse(**metrics)


@router.get("/users", response_model=UserAdminListResponse)
def list_users(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserAdminListResponse:
    users = UserService(db).list_users()
    return UserAdminListResponse(
        users=[
            UserAdminItem(
                id=user.id,
                email=user.email,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
            )
            for user in users
        ]
    )


@router.post("/users/{user_id}/block", response_model=UserAdminItem)
def block_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserAdminItem:
    if admin.id == user_id:
        raise HTTPException(status_code=400, detail="Admin cannot block self")

    service = UserService(db)
    try:
        user = service.update_status(user_id, "blocked")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ActivityLogService(db).log(
        admin_user_id=admin.id,
        action_type="user_block",
        target_entity_type="user",
        target_entity_id=str(user.id),
        description=f"Blocked user {user.email}",
    )

    return UserAdminItem(
        id=user.id,
        email=user.email,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
    )


@router.post("/users/{user_id}/unblock", response_model=UserAdminItem)
def unblock_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UserAdminItem:
    service = UserService(db)
    try:
        user = service.update_status(user_id, "active")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ActivityLogService(db).log(
        admin_user_id=admin.id,
        action_type="user_unblock",
        target_entity_type="user",
        target_entity_id=str(user.id),
        description=f"Unblocked user {user.email}",
    )

    return UserAdminItem(
        id=user.id,
        email=user.email,
        role=user.role,
        status=user.status,
        created_at=user.created_at,
    )


@router.post("/files/upload", response_model=UploadedFileItem)
def upload_file(
    request: Request,
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UploadedFileItem:
    file_service = FileService(db)
    try:
        uploaded = file_service.save_upload(file, admin)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    indexing = IndexingService(db, request.app.state.vector_store, request.app.state.embedder)
    indexing.rebuild_index()

    ActivityLogService(db).log(
        admin_user_id=admin.id,
        action_type="file_upload",
        target_entity_type="uploaded_file",
        target_entity_id=str(uploaded.id),
        description=f"Uploaded {uploaded.original_name}",
    )

    chunk_count = len(file_service.get_chunks_for_file(uploaded.id, limit=100000))
    return UploadedFileItem(
        id=uploaded.id,
        original_name=uploaded.original_name,
        mime_type=uploaded.mime_type,
        size_bytes=uploaded.size_bytes,
        chunk_count=chunk_count,
        uploader_id=uploaded.uploader_id,
        uploaded_at=uploaded.uploaded_at,
    )


@router.get("/files", response_model=UploadedFileListResponse)
def list_files(
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> UploadedFileListResponse:
    rows = FileService(db).list_files()
    return UploadedFileListResponse(
        files=[
            UploadedFileItem(
                id=file_obj.id,
                original_name=file_obj.original_name,
                mime_type=file_obj.mime_type,
                size_bytes=file_obj.size_bytes,
                chunk_count=int(chunk_count),
                uploader_id=file_obj.uploader_id,
                uploaded_at=file_obj.uploaded_at,
            )
            for file_obj, chunk_count in rows
        ]
    )


@router.delete("/files/{file_id}")
def delete_file(
    file_id: int,
    request: Request,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    service = FileService(db)
    try:
        deleted = service.delete_file(file_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    indexing = IndexingService(db, request.app.state.vector_store, request.app.state.embedder)
    indexing.rebuild_index()

    ActivityLogService(db).log(
        admin_user_id=admin.id,
        action_type="file_delete",
        target_entity_type="uploaded_file",
        target_entity_id=str(file_id),
        description=f"Deleted {deleted.original_name}",
    )
    return {"message": "File deleted"}


@router.get("/files/{file_id}/chunks", response_model=FileChunkPreviewResponse)
def preview_chunks(
    file_id: int,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> FileChunkPreviewResponse:
    service = FileService(db)
    try:
        chunks = service.get_chunks_for_file(file_id, limit=100)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return FileChunkPreviewResponse(
        file_id=file_id,
        chunks=[
            FileChunkPreviewItem(
                id=chunk.id,
                chunk_index=chunk.chunk_index,
                preview_text=chunk.chunk_text[:500],
            )
            for chunk in chunks
        ],
    )


@router.post("/reindex")
def reindex(
    request: Request,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    indexing = IndexingService(db, request.app.state.vector_store, request.app.state.embedder)
    records = indexing.rebuild_index()

    ActivityLogService(db).log(
        admin_user_id=admin.id,
        action_type="reindex",
        target_entity_type="vector_index",
        target_entity_id=None,
        description=f"Rebuilt index with {records} records",
    )
    return {"indexed_records": records}


@router.get("/logs", response_model=AdminLogListResponse)
def logs(
    limit: int = 50,
    _: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
) -> AdminLogListResponse:
    stmt = (
        select(AdminActivityLog)
        .order_by(AdminActivityLog.created_at.desc())
        .limit(min(max(limit, 1), 200))
    )
    entries = list(db.scalars(stmt).all())
    return AdminLogListResponse(
        logs=[
            AdminLogItem(
                id=entry.id,
                admin_user_id=entry.admin_user_id,
                action_type=entry.action_type,
                target_entity_type=entry.target_entity_type,
                target_entity_id=entry.target_entity_id,
                description=entry.description,
                created_at=entry.created_at,
            )
            for entry in entries
        ]
    )
