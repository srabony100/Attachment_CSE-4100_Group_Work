"use client";

import { useEffect, useState } from "react";

import { blockUser, listAdminUsers, type AdminUserItem, unblockUser } from "@/lib/admin-api";

export default function AdminUsersPage() {
    const [users, setUsers] = useState<AdminUserItem[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [loadingUserId, setLoadingUserId] = useState<number | null>(null);

    async function loadUsers() {
        const payload = await listAdminUsers();
        setUsers(payload.users);
    }

    useEffect(() => {
        async function load() {
            try {
                await loadUsers();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load users");
            }
        }
        void load();
    }, []);

    async function toggleStatus(user: AdminUserItem) {
        setLoadingUserId(user.id);
        setError(null);
        try {
            if (user.status === "blocked") {
                await unblockUser(user.id);
            } else {
                await blockUser(user.id);
            }
            await loadUsers();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Status update failed");
        } finally {
            setLoadingUserId(null);
        }
    }

    return (
        <div className="space-y-6">
            <h1 className="font-display text-4xl">User Management</h1>
            {error ? <p className="text-sm text-red-300">{error}</p> : null}

            <div className="rounded-2xl border border-white/15 bg-white/5 p-5 backdrop-blur-xl">
                <div className="space-y-3">
                    {users.map((user) => (
                        <article key={user.id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-black/20 p-4">
                            <div>
                                <p className="text-sm text-slate-200">{user.email}</p>
                                <p className="text-xs text-slate-400">
                                    {user.role} • {user.status} • {new Date(user.created_at).toLocaleDateString()}
                                </p>
                            </div>
                            {user.role !== "admin" ? (
                                <button
                                    type="button"
                                    disabled={loadingUserId === user.id}
                                    onClick={() => void toggleStatus(user)}
                                    className={`rounded-xl px-4 py-2 text-xs font-semibold ${user.status === "blocked"
                                        ? "border border-emerald-300/30 text-emerald-200 hover:bg-emerald-400/10"
                                        : "border border-red-300/30 text-red-200 hover:bg-red-400/10"
                                        }`}
                                >
                                    {user.status === "blocked" ? "Unblock" : "Block"}
                                </button>
                            ) : (
                                <span className="rounded-xl border border-cyan-300/30 px-4 py-2 text-xs text-cyan-200">Admin</span>
                            )}
                        </article>
                    ))}
                </div>
            </div>
        </div>
    );
}
