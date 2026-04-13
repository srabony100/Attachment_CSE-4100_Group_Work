import { apiRequest } from "@/lib/api-client";

export type AuthUser = {
    id: number;
    email: string;
    role: "admin" | "user";
    status: "active" | "blocked";
    created_at: string;
};

export type AuthResponse = {
    message: string;
    user: AuthUser;
};

export function registerUser(email: string, password: string) {
    return apiRequest<AuthResponse>("/auth/register", {
        method: "POST",
        body: { email, password },
    });
}

export function loginUser(email: string, password: string) {
    return apiRequest<AuthResponse>("/auth/login", {
        method: "POST",
        body: { email, password },
    });
}

export function loginAdmin(email: string, password: string) {
    return apiRequest<AuthResponse>("/admin/login", {
        method: "POST",
        body: { email, password },
    });
}

export function logoutUser() {
    return apiRequest<{ message: string }>("/auth/logout", { method: "POST" });
}

export function getCurrentUser() {
    return apiRequest<AuthUser>("/auth/me");
}
