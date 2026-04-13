"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import ProtectedGate from "@/components/auth/protected-gate";
import { getMyHistory, type HistoryItem } from "@/lib/history-api";

export default function HistoryPage() {
    const [items, setItems] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            setLoading(true);
            setError(null);
            try {
                const payload = await getMyHistory(40);
                setItems(payload.items);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load history");
            } finally {
                setLoading(false);
            }
        }
        void load();
    }, []);

    return (
        <ProtectedGate>
            <main className="mx-auto min-h-screen w-full max-w-5xl px-6 py-8 text-slate-100">
                <header className="mb-6 flex items-center justify-between">
                    <h1 className="font-display text-4xl">Your Search History</h1>
                    <Link href="/search" className="rounded-full border border-white/20 px-4 py-2 text-sm hover:bg-white/10">
                        Back to Search
                    </Link>
                </header>

                {loading ? <p className="text-sm text-slate-400">Loading history...</p> : null}
                {error ? <p className="text-sm text-red-300">{error}</p> : null}

                {!loading && !error ? (
                    <div className="space-y-3">
                        {items.map((item) => (
                            <article key={item.id} className="rounded-2xl border border-white/15 bg-white/5 p-4 backdrop-blur-xl">
                                <p className="text-sm text-slate-200">{item.query_text}</p>
                                <p className="mt-2 text-xs text-slate-400">Top match: {item.result_title ?? "No match"}</p>
                                <p className="mt-1 text-xs text-slate-500">{new Date(item.created_at).toLocaleString()}</p>
                            </article>
                        ))}
                        {items.length === 0 ? <p className="text-sm text-slate-400">No searches yet.</p> : null}
                    </div>
                ) : null}
            </main>
        </ProtectedGate>
    );
}
