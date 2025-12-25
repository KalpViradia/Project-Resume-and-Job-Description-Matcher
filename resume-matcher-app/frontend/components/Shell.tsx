"use client";

import React from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

interface ShellProps {
    children: React.ReactNode;
}

import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

export const Shell = ({ children }: ShellProps) => {
    const pathname = usePathname();
    const router = useRouter();

    useEffect(() => {
        const token = localStorage.getItem("token");
        // Access Control Logic:
        // If not logged in, only allowed to use the matcher route (and public routes like login/signup)
        // Since this Shell wraps the dashboard (matcher, history, settings, etc.)
        // We assume login/signup are OUTSIDE this Shell (because they have their own layout or page structure?)
        // Let's verify: signup/login use root layout or their own? Usually separate.
        // Assuming Shell is used for dashboard routes.

        // Allowed public routes inside Shell? Maybe none if Shell assumes "Dashboard".
        // But user said: "user who is not logged in is only allowed to use the matcher route"
        // So /matcher IS allowed without token.

        // Protected routes: Everything else (e.g. /past-matches, /settings)

        const isPublicRoute = pathname === "/matcher" || pathname === "/matcher/";

        if (!token && !isPublicRoute) {
            router.push("/login");
        }
    }, [pathname, router]);

    return (
        <div className="flex min-h-screen flex-col">
            <Header />
            <div className="flex flex-1 pt-16">
                <Sidebar />
                <main className="flex-1 md:pl-64 w-full">
                    <div className="p-6 max-w-7xl mx-auto w-full">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
};
