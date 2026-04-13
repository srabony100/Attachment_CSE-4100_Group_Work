import { NextRequest, NextResponse } from "next/server";

const userProtected = ["/search", "/history"];
const adminProtected = ["/admin/dashboard", "/admin/files", "/admin/users", "/admin/logs"];

function needsGuard(pathname: string): { type: "user" | "admin" } | null {
    if (adminProtected.some((path) => pathname.startsWith(path))) {
        return { type: "admin" };
    }
    if (userProtected.some((path) => pathname.startsWith(path))) {
        return { type: "user" };
    }
    return null;
}

export function middleware(request: NextRequest) {
    const guard = needsGuard(request.nextUrl.pathname);
    if (!guard) {
        return NextResponse.next();
    }

    const token = request.cookies.get("access_token")?.value;
    const role = request.cookies.get("user_role")?.value;
    if (!token) {
        const loginPath = guard.type === "admin" ? "/admin/login" : "/login";
        const url = new URL(loginPath, request.url);
        url.searchParams.set("next", request.nextUrl.pathname);
        return NextResponse.redirect(url);
    }

    if (guard.type === "admin" && role !== "admin") {
        return NextResponse.redirect(new URL("/search", request.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: ["/search/:path*", "/history/:path*", "/admin/dashboard/:path*", "/admin/files/:path*", "/admin/users/:path*", "/admin/logs/:path*"],
};
