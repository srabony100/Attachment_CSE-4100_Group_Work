"use client";

import { useEffect, useState } from "react";

import { fetchAnalytics, type DashboardAnalytics, listAdminLogs } from "@/lib/admin-api";

const statConfig: Array<{ key: keyof DashboardAnalytics; label: string }> = [
    { key: "total_users", label: "Total Users" },
    { key: "active_users", label: "Active Users" },
    { key: "blocked_users", label: "Blocked Users" },
    { key: "total_uploaded_files", label: "Uploaded Files" },
    { key: "total_indexed_chunks", label: "Indexed Chunks" },
    { key: "total_searches", label: "Total Searches" },
    { key: "recent_admin_activities", label: "Admin Actions (7d)" },
    { key: "recent_uploads", label: "Uploads (7d)" },
];

export default function AdminDashboardPage() {
    const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
    const [recentCount, setRecentCount] = useState(0);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        async function load() {
            try {
                const [metrics, logs] = await Promise.all([fetchAnalytics(), listAdminLogs(10)]);
                setAnalytics(metrics);
                setRecentCount(logs.logs.length);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            }
        }
        void load();
    }, []);

    if (error) {
        return <p className="text-sm text-red-300">{error}</p>;
    }

    if (!analytics) {
        return <p className="text-sm text-slate-400">Loading analytics...</p>;
    }

    return (
        <div className="space-y-6">
            <header>
                <h1 className="font-display text-4xl">Dashboard Analytics</h1>
                <p className="mt-2 text-sm text-slate-400">Recent activities shown: {recentCount}</p>
            </header>

            <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                {statConfig.map((stat) => (
                    <article key={stat.key} className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                        <p className="text-xs uppercase tracking-wide text-slate-400">{stat.label}</p>
                        <p className="mt-3 font-display text-4xl">{analytics[stat.key]}</p>
                    </article>
                ))}
            </section>
        </div>
    );
}
