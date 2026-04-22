"use client";

import React from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { LayoutDashboard, History, Settings, MessageCircle, GitCompare } from "lucide-react";

export const Sidebar = () => {
    const pathname = usePathname();

    const menuItems = [
        {
            name: "Dashboard",
            path: "/matcher",
            icon: <LayoutDashboard className="w-5 h-5 mr-3" />,
        },
        {
            name: "History",
            path: "/past-matches",
            icon: <History className="w-5 h-5 mr-3" />,
        },
        {
            name: "Chat Assistant",
            path: "/chat",
            icon: <MessageCircle className="w-5 h-5 mr-3" />,
        },
        {
            name: "Compare Resumes",
            path: "/compare",
            icon: <GitCompare className="w-5 h-5 mr-3" />,
        },
    ];

    return (
        <div className="hidden border-r bg-background md:block w-64 fixed h-full pt-16 top-0 z-30">
            <div className="space-y-4 py-4">
                <div className="px-3 py-2">
                    <div className="space-y-1">
                        {menuItems.map((item) => {
                            const isActive = pathname === item.path;
                            return (
                                <Button
                                    key={item.name}
                                    variant={isActive ? "secondary" : "ghost"}
                                    asChild
                                    className={cn(
                                        "w-full justify-start",
                                        isActive && "bg-secondary"
                                    )}
                                >
                                    <Link href={item.path}>
                                        {item.icon}
                                        {item.name}
                                    </Link>
                                </Button>
                            );
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};
