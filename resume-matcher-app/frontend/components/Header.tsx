"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
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

    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

    return (
        <header className="fixed top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex h-16 items-center px-4 sm:px-6 justify-between">
                <div className="flex items-center gap-2 font-bold text-xl">
                    <Image 
                        src="/icon.png" 
                        alt="Resume Matcher Logo" 
                        width={32} 
                        height={32} 
                        className="rounded-lg shadow-sm object-cover" 
                        priority 
                    />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-700 dark:from-blue-400 dark:to-indigo-400 hidden sm:inline-block">
                        Resume Matcher
                    </span>
                </div>

                <div className="flex items-center gap-3 relative">
                    <div className="hidden md:flex items-center gap-4">
                        {isLoggedIn ? (
                            <div className="flex items-center gap-4">
                                <span className="text-sm font-medium">Hello, {userName || "User"}</span>
                                <Button variant="destructive" size="sm" onClick={handleLogout}>Log Out</Button>
                            </div>
                        ) : (
                            <div className="flex gap-2">
                                <Button variant="ghost" size="sm" asChild><Link href="/login">Log In</Link></Button>
                                <Button size="sm" asChild className="bg-gradient-to-r from-blue-600 to-indigo-600"><Link href="/signup">Sign Up</Link></Button>
                            </div>
                        )}
                    </div>

                    {/* Mobile Hamburger Toggle */}
                    <div className="md:hidden flex items-center">
                        <Button 
                            variant="ghost" 
                            size="icon" 
                            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                            aria-label="Toggle Menu"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
                        </Button>
                    </div>

                    {/* Mobile Dropdown Menu */}
                    {isMobileMenuOpen && (
                        <div className="absolute top-14 right-0 w-64 bg-background border rounded-lg shadow-xl p-4 flex flex-col gap-4 md:hidden animate-in fade-in slide-in-from-top-2">
                            <div className="flex flex-col gap-2">
                                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Navigation</span>
                                <Link href="/matcher" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium p-2 hover:bg-muted rounded-md transition-colors">Dashboard</Link>
                                <Link href="/past-matches" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium p-2 hover:bg-muted rounded-md transition-colors">History</Link>
                                <Link href="/chat" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium p-2 hover:bg-muted rounded-md transition-colors">Chat Assistant</Link>
                                <Link href="/compare" onClick={() => setIsMobileMenuOpen(false)} className="text-sm font-medium p-2 hover:bg-muted rounded-md transition-colors">Compare Resumes</Link>
                            </div>

                            <div className="h-px bg-border w-full" />

                            <div className="flex flex-col gap-2">
                                {isLoggedIn ? (
                                    <>
                                        <span className="text-sm font-medium p-2">Hey, {userName || "User"}</span>
                                        <Button variant="destructive" size="sm" onClick={() => { handleLogout(); setIsMobileMenuOpen(false); }} className="w-full">Log Out</Button>
                                    </>
                                ) : (
                                    <>
                                        <Button variant="outline" size="sm" asChild onClick={() => setIsMobileMenuOpen(false)} className="w-full"><Link href="/login">Log In</Link></Button>
                                        <Button size="sm" asChild onClick={() => setIsMobileMenuOpen(false)} className="w-full bg-gradient-to-r from-blue-600 to-indigo-600"><Link href="/signup">Sign Up</Link></Button>
                                    </>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
};
