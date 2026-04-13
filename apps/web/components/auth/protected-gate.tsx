"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useAuth } from "@/context/auth-context";

type ProtectedGateProps = {
    children: React.ReactNode;
    requireAdmin?: boolean;
};

export default function ProtectedGate({ children, requireAdmin = false }: ProtectedGateProps) {
    const { isAuthenticated, loading, role } = useAuth();
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        if (loading) {
            return;
        }
        if (!isAuthenticated) {
            const target = requireAdmin ? "/admin/login" : "/login";
            router.replace(`${target}?next=${encodeURIComponent(pathname)}`);
            return;
        }
        if (requireAdmin && role !== "admin") {
            router.replace("/search");
        }
    }, [isAuthenticated, loading, requireAdmin, role, router, pathname]);

    if (loading || !isAuthenticated || (requireAdmin && role !== "admin")) {
        return (
            <div className="flex min-h-screen items-center justify-center text-sm text-slate-300">
                Checking your session...
            </div>
        );
    }

    return <>{children}</>;
}
