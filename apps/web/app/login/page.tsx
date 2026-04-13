"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

import AuthShell from "@/components/auth/auth-shell";
import { ApiError } from "@/lib/api-client";
import { useAuth } from "@/context/auth-context";

function LoginContent() {
    const { loginUser, registerUser } = useAuth();
    const router = useRouter();
    const params = useSearchParams();

    const [mode, setMode] = useState<"login" | "register">("login");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const nextPath = useMemo(() => params.get("next") || "/search", [params]);

    async function onSubmit(event: FormEvent) {
        event.preventDefault();
        setLoading(true);
        setError(null);
        try {
            if (mode === "login") {
                await loginUser(email, password);
            } else {
                await registerUser(email, password);
            }
            router.replace(nextPath);
        } catch (err) {
            if (err instanceof ApiError) {
                setError(err.message);
            } else if (err instanceof Error) {
                setError(err.message);
            } else {
                setError("Authentication failed");
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <AuthShell
            title="Welcome back"
            subtitle="Login to use semantic search. New users can register here, but admin accounts are seeded through backend configuration only."
        >
            <div className="grid gap-6 md:grid-cols-[1fr_1fr]">
                <form onSubmit={onSubmit} className="rounded-3xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">
                    <div className="mb-4 flex gap-2 rounded-full bg-slate-900/60 p-1 text-xs">
                        <button
                            type="button"
                            onClick={() => setMode("login")}
                            className={`flex-1 rounded-full px-4 py-2 ${mode === "login" ? "bg-cyan-300 text-slate-900" : "text-slate-200"}`}
                        >
                            Login
                        </button>
                        <button
                            type="button"
                            onClick={() => setMode("register")}
                            className={`flex-1 rounded-full px-4 py-2 ${mode === "register" ? "bg-cyan-300 text-slate-900" : "text-slate-200"}`}
                        >
                            Register
                        </button>
                    </div>

                    <label className="text-sm text-slate-200">Email</label>
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
                        minLength={8}
                        required
                        className="mt-2 w-full rounded-xl border border-white/20 bg-slate-950/60 px-4 py-3 text-sm"
                    />

                    {error ? <p className="mt-4 text-sm text-red-300">{error}</p> : null}

                    <button
                        type="submit"
                        disabled={loading}
                        className="mt-6 w-full rounded-xl bg-cyan-300 px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-cyan-200 disabled:opacity-70"
                    >
                        {loading ? "Please wait..." : mode === "login" ? "Login" : "Create account"}
                    </button>
                </form>

                <div className="rounded-3xl border border-white/20 bg-white/10 p-6 backdrop-blur-xl">
                    <h2 className="font-display text-2xl">Secure by design</h2>
                    <ul className="mt-4 space-y-3 text-sm text-slate-300">
                        <li>Password hashing with bcrypt/passlib</li>
                        <li>JWT session cookies for authenticated requests</li>
                        <li>Blocked users cannot login or query</li>
                        <li>Admin endpoints protected by backend role checks</li>
                    </ul>
                    <p className="mt-8 text-sm text-slate-400">
                        Admin access? Use the dedicated <Link href="/admin/login" className="text-cyan-200 underline">admin login</Link> route.
                    </p>
                </div>
            </div>
        </AuthShell>
    );
}

export default function LoginPage() {
    return (
        <Suspense fallback={<main className="min-h-screen text-slate-100" />}>
            <LoginContent />
        </Suspense>
    );
}
