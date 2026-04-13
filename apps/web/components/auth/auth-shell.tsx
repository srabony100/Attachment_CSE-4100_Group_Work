"use client";

import Link from "next/link";

import { useAuth } from "@/context/auth-context";

type AuthShellProps = {
    title: string;
    subtitle: string;
    children: React.ReactNode;
};

export default function AuthShell({ title, subtitle, children }: AuthShellProps) {
    const { isAuthenticated, user, logout } = useAuth();

    return (
        <main className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
            <div className="pointer-events-none absolute -left-24 top-10 h-72 w-72 rounded-full bg-cyan-400/20 blur-3xl" />
            <div className="pointer-events-none absolute right-0 top-64 h-96 w-96 rounded-full bg-emerald-400/15 blur-3xl" />

            <header className="relative mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-6">
                <Link href="/" className="font-display text-2xl tracking-tight text-white">
                    CodeSense
                </Link>
                <nav className="flex items-center gap-3 text-sm">
                    <Link href="/" className="rounded-full border border-white/20 px-4 py-2 text-slate-200 hover:bg-white/10">
                        Home
                    </Link>
                    {isAuthenticated ? (
                        <>
                            <Link href="/search" className="rounded-full border border-cyan-300/50 px-4 py-2 text-cyan-200 hover:bg-cyan-400/10">
                                Search
                            </Link>
                            <button
                                type="button"
                                onClick={() => void logout()}
                                className="rounded-full border border-red-300/40 px-4 py-2 text-red-200 hover:bg-red-400/10"
                            >
                                Logout {user?.email}
                            </button>
                        </>
                    ) : null}
                </nav>
            </header>

            <section className="relative mx-auto w-full max-w-6xl px-6 pb-20 pt-8">
                <div className="mb-8">
                    <h1 className="font-display text-4xl text-white md:text-5xl">{title}</h1>
                    <p className="mt-3 max-w-2xl text-slate-300">{subtitle}</p>
                </div>
                {children}
            </section>
        </main>
    );
    
}
