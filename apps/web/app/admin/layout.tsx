"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import ProtectedGate from "@/components/auth/protected-gate";
import { useAuth } from "@/context/auth-context";

const navLinks = [
    { href: "/admin/dashboard", label: "Dashboard" },
    { href: "/admin/files", label: "Files" },
    { href: "/admin/users", label: "Users" },
    { href: "/admin/logs", label: "Logs" },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
    const pathname = usePathname();
    const { logout } = useAuth();

    // Do not guard the login page with admin-only checks.
    if (pathname.startsWith("/admin/login")) {
        return <>{children}</>;
    }

    return (
        <ProtectedGate requireAdmin>
            <main className="min-h-screen bg-slate-950 text-slate-100">
                <div className="mx-auto flex w-full max-w-7xl gap-6 px-6 py-8">
                    <aside className="hidden w-64 rounded-3xl border border-white/15 bg-white/5 p-4 backdrop-blur-xl md:block">
                        <p className="font-display mb-4 text-xl">Admin Console</p>
                        <nav className="space-y-2 text-sm">
                            {navLinks.map((item) => (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={`block rounded-xl px-3 py-2 ${pathname === item.href ? "bg-cyan-300 text-slate-950" : "hover:bg-white/10"}`}
                                >
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                        <button
                            type="button"
                            onClick={() => void logout()}
                            className="mt-6 w-full rounded-xl border border-red-300/30 px-3 py-2 text-sm text-red-200 hover:bg-red-500/10"
                        >
                            Logout
                        </button>
                    </aside>

                    <section className="w-full">{children}</section>
                </div>
            </main>
        </ProtectedGate>
    );
}
