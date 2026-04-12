"use client";

import { useEffect, useState } from "react";

import { listAdminLogs, type AdminLogItem } from "@/lib/admin-api";

export default function AdminLogsPage() {
    const [logs, setLogs] = useState<AdminLogItem[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                const payload = await listAdminLogs(80);
                setLogs(payload.logs);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load logs");
            }
        }
        void load();
    }, []);

    return (
        <div className="space-y-6">
            <h1 className="font-display text-4xl">Admin Activity Logs</h1>
            {error ? <p className="text-sm text-red-300">{error}</p> : null}

            <section className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                <div className="space-y-3">
                    {logs.map((log) => (
                        <article key={log.id} className="rounded-xl border border-white/10 bg-black/20 p-4">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                                <p className="text-sm text-slate-100">{log.action_type}</p>
                                <p className="text-xs text-slate-400">{new Date(log.created_at).toLocaleString()}</p>
                            </div>
                            <p className="mt-1 text-xs text-cyan-200">
                                target: {log.target_entity_type}#{log.target_entity_id ?? "-"}
                            </p>
                            <p className="mt-2 text-sm text-slate-300">{log.description}</p>
                        </article>
                    ))}
                    {logs.length === 0 ? <p className="text-sm text-slate-400">No admin activities yet.</p> : null}
                </div>
            </section>
        </div>
    );
}
