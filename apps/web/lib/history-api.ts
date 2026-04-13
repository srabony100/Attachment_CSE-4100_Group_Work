import { apiRequest } from "@/lib/api-client";

export type HistoryItem = {
    id: number;
    query_text: string;
    result_record_id: string | null;
    result_title: string | null;
    created_at: string;
};

export type HistoryResponse = {
    items: HistoryItem[];
};

export function getMyHistory(limit = 25) {
    return apiRequest<HistoryResponse>(`/history?limit=${limit}`);
}
