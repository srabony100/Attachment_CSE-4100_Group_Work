import { apiRequest, apiUpload } from "@/lib/api-client";

export type AdminUserItem = {
    id: number;
    email: string;
    role: string;
    status: string;
    created_at: string;
};

export type UploadedFileItem = {
    id: number;
    original_name: string;
    mime_type: string;
    size_bytes: number;
    chunk_count: number;
    uploader_id: number;
    uploaded_at: string;
};

export type FileChunkPreviewItem = {
    id: number;
    chunk_index: number;
    preview_text: string;
};

export type AdminLogItem = {
    id: number;
    admin_user_id: number;
    action_type: string;
    target_entity_type: string;
    target_entity_id: string | null;
    description: string;
    created_at: string;
};

export type DashboardAnalytics = {
    total_users: number;
    active_users: number;
    blocked_users: number;
    total_uploaded_files: number;
    total_indexed_chunks: number;
    total_searches: number;
    recent_admin_activities: number;
    recent_uploads: number;
};

export function fetchAnalytics() {
    return apiRequest<DashboardAnalytics>("/admin/dashboard/analytics");
}

export async function uploadAdminFile(file: File) {
    const formData = new FormData();
    formData.append("file", file);
    return apiUpload<UploadedFileItem>("/admin/files/upload", formData);
}

export function listAdminFiles() {
    return apiRequest<{ files: UploadedFileItem[] }>("/admin/files");
}

export function deleteAdminFile(fileId: number) {
    return apiRequest<{ message: string }>(`/admin/files/${fileId}`, { method: "DELETE" });
}

export function previewFileChunks(fileId: number) {
    return apiRequest<{ file_id: number; chunks: FileChunkPreviewItem[] }>(`/admin/files/${fileId}/chunks`);
}

export function reindexFiles() {
    return apiRequest<{ indexed_records: number }>("/admin/reindex", { method: "POST" });
}

export function listAdminUsers() {
    return apiRequest<{ users: AdminUserItem[] }>("/admin/users");
}

export function blockUser(userId: number) {
    return apiRequest<AdminUserItem>(`/admin/users/${userId}/block`, { method: "POST" });
}

export function unblockUser(userId: number) {
    return apiRequest<AdminUserItem>(`/admin/users/${userId}/unblock`, { method: "POST" });
}

export function listAdminLogs(limit = 50) {
    return apiRequest<{ logs: AdminLogItem[] }>(`/admin/logs?limit=${limit}`);
}
