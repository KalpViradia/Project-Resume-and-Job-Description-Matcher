"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { format } from "date-fns";

interface MatchHistoryItem {
    id: string; // Prisma uses CUID/UUID usually, assuming string
    jobDescription: string;
    matchScore: number;
    matchedSkills: string[];
    missingSkills: string[]; // Although valid in backend, might not be displayed or used here
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
                // If no token, maybe redirect or show empty
                setLoading(false);
                return;
            }

            try {
                const res = await fetch("http://localhost:5000/api/history", {
                    headers: {
                        "x-auth-token": token // Expected by auth middleware usually, need to check middleware but standard is x-auth-token or Authorization
                    }
                });

                if (!res.ok) {
                    throw new Error("Failed to fetch history");
                }

                const data = await res.json();
                // Backend returns array
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

    if (loading) return <div className="p-8 text-center">Loading history...</div>;
    // We can use a Skeleton here later

    return (
        <div className="space-y-6 max-w-4xl mx-auto">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-primary">Match History</h1>
                <p className="text-muted-foreground">View your past resume matches and insights.</p>
            </div>

            {error && <div className="text-destructive">{error}</div>}

            {!loading && history.length === 0 && (
                <Card className="text-center p-8">
                    <p className="text-muted-foreground">No matches found. Go to Dashboard to scan a resume!</p>
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
