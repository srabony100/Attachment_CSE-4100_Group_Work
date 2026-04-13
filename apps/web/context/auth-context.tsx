"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ApiError } from "@/lib/api-client";
import {
    type AuthUser,
    getCurrentUser,
    loginAdmin as loginAdminApi,
    loginUser as loginUserApi,
    logoutUser as logoutUserApi,
    registerUser as registerUserApi,
} from "@/lib/auth-api";

type AuthContextType = {
    user: AuthUser | null;
    role: "admin" | "user" | null;
    isAuthenticated: boolean;
    loading: boolean;
    refreshSession: () => Promise<void>;
    loginUser: (email: string, password: string) => Promise<void>;
    loginAdmin: (email: string, password: string) => Promise<void>;
    registerUser: (email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);

    const refreshSession = useCallback(async () => {
        try {
            const me = await getCurrentUser();
            setUser(me);
        } catch (error) {
            if (error instanceof ApiError && (error.status === 401 || error.status === 403)) {
                setUser(null);
                return;
            }
            setUser(null);
        }
    }, []);

    useEffect(() => {
        async function load() {
            setLoading(true);
            await refreshSession();
            setLoading(false);
        }
        void load();
    }, [refreshSession]);

    const loginUser = useCallback(async (email: string, password: string) => {
        const payload = await loginUserApi(email, password);
        setUser(payload.user);
    }, []);

    const loginAdmin = useCallback(async (email: string, password: string) => {
        const payload = await loginAdminApi(email, password);
        setUser(payload.user);
    }, []);

    const registerUser = useCallback(async (email: string, password: string) => {
        const payload = await registerUserApi(email, password);
        setUser(payload.user);
    }, []);

    const logout = useCallback(async () => {
        await logoutUserApi();
        setUser(null);
    }, []);

    const value = useMemo<AuthContextType>(
        () => ({
            user,
            role: user?.role ?? null,
            isAuthenticated: Boolean(user),
            loading,
            refreshSession,
            loginUser,
            loginAdmin,
            registerUser,
            logout,
        }),
        [user, loading, refreshSession, loginUser, loginAdmin, registerUser, logout],
    );

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within AuthProvider");
    }
    return context;
    
}
