"use client";

import { FormEvent, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import AuthShell from "@/components/auth/auth-shell";
import { ApiError } from "@/lib/api-client";
import { useAuth } from "@/context/auth-context";

function AdminLoginContent() {
    const { loginAdmin } = useAuth();
    const router = useRouter();
    const params = useSearchParams();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const nextPath = useMemo(() => params.get("next") || "/admin/dashboard", [params]);

    async function onSubmit(event: FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await loginAdmin(email, password);
            router.replace(nextPath);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else {
                setError("Admin login failed");
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <AuthShell
            title="Admin control portal"
            subtitle="Only pre-seeded admin accounts can login here. There is no public admin registration."
        >
            <form onSubmit={onSubmit} className="max-w-xl rounded-3xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">
                <label className="text-sm text-slate-200">Admin email</label>
                <input
                    type="email"
                    value={email}
                    onChange={(event) => setEmail(event.target.value)}
                    required
                    className="mt-2 w-full rounded-xl border border-white/20 bg-slate-950/60 px-4 py-3 text-sm"
                />

                <label className="mt-4 block text-sm text-slate-200">Password</label>
                <input
                    type="password"
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    minLength={8}
                    className="mt-2 w-full rounded-xl border border-white/20 bg-slate-950/60 px-4 py-3 text-sm"
                />

                {error ? <p className="mt-4 text-sm text-red-300">{error}</p> : null}

                <button
                    type="submit"
                    disabled={loading}
                    className="mt-6 w-full rounded-xl bg-cyan-300 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-200 disabled:opacity-70"
                >
                    {loading ? "Signing in..." : "Sign in as admin"}
                </button>
            </form>
        </AuthShell>
    );
}

export default function AdminLoginPage() {
    return (
        <Suspense fallback={<main className="min-h-screen text-slate-100" />}>
            <AdminLoginContent />
        </Suspense>
    );
    
}
