"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export const Header = () => {
    const router = useRouter();
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userName, setUserName] = useState("");

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem("token");
            if (token) {
                setIsLoggedIn(true);
                try {
                    const res = await fetch("http://localhost:5000/api/auth/user", {
                        headers: { "x-auth-token": token }
                    });
                    if (res.ok) {
                        const user = await res.json();
                        setUserName(user.name);
                    } else {
                        // Token invalid/expired
                        localStorage.removeItem("token");
                        setIsLoggedIn(false);
                    }
                } catch (err) {
                    console.error("Failed to fetch user", err);
                }
            }
        };
        checkAuth();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("token");
        setIsLoggedIn(false);
        setUserName("");
        router.push("/login");
    };

    return (
        <header className="fixed top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-16 items-center px-4 sm:px-6">
                <div className="flex items-center gap-2 font-bold text-xl mr-auto">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-500 to-indigo-600 flex items-center justify-center text-white text-sm font-bold">
                        M
                    </div>
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-700 dark:from-blue-400 dark:to-indigo-400">
                        Resume Matcher
                    </span>
                </div>

                <div className="flex items-center gap-4">
                    {isLoggedIn ? (
                        <div className="flex items-center gap-4">
                            <span className="text-sm font-medium hidden sm:inline-block">
                                Hello, {userName || "User"}
                            </span>
                            <Button
                                variant="destructive"
                                size="sm"
                                onClick={handleLogout}
                            >
                                Log Out
                            </Button>
                        </div>
                    ) : (
                        <div className="flex gap-2">
                            <Button variant="ghost" size="sm" asChild>
                                <Link href="/login">Log In</Link>
                            </Button>
                            <Button size="sm" asChild className="bg-gradient-to-r from-blue-600 to-indigo-600">
                                <Link href="/signup">Sign Up</Link>
                            </Button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};
