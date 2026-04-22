"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { format } from "date-fns";
import Link from "next/link";
import { Search, Loader2 } from "lucide-react";

interface MatchHistoryItem {
    id: string;
    jobDescription: string;
    matchScore: number;
    matchedSkills: string[];
    missingSkills: string[];
    createdAt: string;
}

// Helper to extract role/company from JD if possible, or use generic
const extractTitle = (text: string) => {
    const lines = text.split('\n');
    return lines[0].substring(0, 30) + (lines[0].length > 30 ? "..." : "");
}

export default function HistoryPage() {
    const [history, setHistory] = useState<MatchHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const fetchHistory = async () => {
            const token = localStorage.getItem("token");
            if (!token) {
                setLoading(false);
                return;
            }

            try {
                const res = await fetch("http://localhost:5000/api/history", {
                    headers: {
                        "x-auth-token": token
                    }
                });

                if (!res.ok) {
                    throw new Error("Failed to fetch history");
                }

                const data = await res.json();
                setHistory(data);
            } catch (err) {
                console.error(err);
                setError("Failed to load history.");
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, []);

    if (loading) {
        return (
            <div className="flex items-center justify-center p-16 gap-3 text-muted-foreground">
                <Loader2 className="h-5 w-5 animate-spin" />
                <span>Loading history...</span>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-primary">Match History</h1>
                <p className="text-muted-foreground">View your past resume matches and insights.</p>
            </div>

            {error && <div className="text-destructive">{error}</div>}

            {!loading && history.length === 0 && (
                <Card className="text-center p-8">
                    <div className="flex flex-col items-center gap-4">
                        <div className="p-4 rounded-full bg-muted">
                            <Search className="h-8 w-8 text-muted-foreground" />
                        </div>
                        <div className="space-y-2">
                            <p className="font-medium text-foreground">No matches found yet</p>
                            <p className="text-sm text-muted-foreground">
                                Run your first resume match to see your history here.
                            </p>
                        </div>
                        <Button asChild className="mt-2">
                            <Link href="/matcher">Start New Match</Link>
                        </Button>
                    </div>
                </Card>
            )}

            <div className="grid gap-4">
                {history.map((item) => (
                    <Card key={item.id} className="hover:bg-accent/50 transition-colors">
                        <CardHeader className="pb-2">
                            <div className="flex justify-between items-start">
                                <div>
                                    <CardTitle className="text-xl text-primary">{extractTitle(item.jobDescription)}</CardTitle>
                                    <CardDescription>
                                        Scanned on {format(new Date(item.createdAt), "MMM d, yyyy")}
                                    </CardDescription>
                                </div>
                                <Badge
                                    variant={item.matchScore > 80 ? "default" : item.matchScore > 50 ? "secondary" : "destructive"}
                                    className="text-md px-3 py-1"
                                >
                                    {item.matchScore}% Match
                                </Badge>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-wrap gap-2 mt-2">
                                {item.matchedSkills.map((skill, idx) => (
                                    <Badge key={idx} variant="outline" className="border-primary/20 bg-primary/5">
                                        {skill}
                                    </Badge>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
