export const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
    status: number;

    constructor(message: string, status: number) {
        super(message);
        this.status = status;
    }
}

type RequestOptions = {
    method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
    body?: unknown;
    signal?: AbortSignal;
    headers?: Record<string, string>;
};

export async function apiRequest<T>(path: string, options?: RequestOptions): Promise<T> {
    let response: Response;
    try {
        response = await fetch(`${API_BASE}${path}`, {
            method: options?.method ?? "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(options?.headers ?? {}),
            },
            body: options?.body ? JSON.stringify(options.body) : undefined,
            signal: options?.signal,
        });
    } catch (error) {
        if (options?.signal?.aborted) {
            throw error;
        }
        throw new Error(`Could not reach backend API at ${API_BASE}. Please ensure the API server is running and CORS is configured for this frontend origin.`);
    }

    const maybeJson = await response.text();
    let payload: Record<string, unknown> | null = null;
    try {
        payload = maybeJson ? (JSON.parse(maybeJson) as Record<string, unknown>) : null;
    } catch {
        payload = null;
    }

    if (!response.ok) {
        const detail = (payload?.detail as string | undefined) ?? (payload?.error as string | undefined) ?? "Request failed";
        throw new ApiError(detail, response.status);
    }

    return (payload as T) ?? ({} as T);
}

export async function apiUpload<T>(path: string, formData: FormData): Promise<T> {
    const response = await fetch(`${API_BASE}${path}`, {
        method: "POST",
        credentials: "include",
        body: formData,
    });

    const payload = (await response.json().catch(() => ({}))) as Record<string, unknown>;
    if (!response.ok) {
        const detail = (payload.detail as string | undefined) ?? "Upload failed";
        throw new ApiError(detail, response.status);
    }
    return payload as T;
}
