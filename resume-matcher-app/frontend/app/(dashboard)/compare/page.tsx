"use client";

import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, GitCompare, Trophy, TrendingUp, TrendingDown } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface CompareResult {
    score_a: number;
    score_b: number;
    recommendation: string;
}

export default function ComparePage() {
    const [jd, setJd] = useState("");
    const [resumeA, setResumeA] = useState("");
    const [resumeB, setResumeB] = useState("");
    
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<CompareResult | null>(null);
    const [error, setError] = useState("");

    const handleCompare = async () => {
        if (!jd || !resumeA || !resumeB) {
            setError("Please provide the Job Description and both Resumes.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        const formData = new FormData();
        formData.append("jd_text", jd);
        formData.append("resume_text_input_a", resumeA);
        formData.append("resume_text_input_b", resumeB);

        try {
            const res = await fetch("http://localhost:8000/compare", {
                method: "POST",
                body: formData
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || "Failed to compare resumes");
            }

            const data: CompareResult = await res.json();
            setResult(data);
        } catch (err: any) {
            setError(err.message || "An error occurred during comparison.");
        } finally {
            setLoading(false);
        }
    };

    const getWinnerIndicator = (score: number, otherScore: number) => {
        if (score > otherScore) {
            return <div className="inline-flex items-center gap-1 text-green-500 bg-green-500/10 px-2 py-0.5 rounded text-sm font-semibold mt-2"><Trophy className="w-4 h-4"/> Winner</div>;
        } else if (score < otherScore) {
            return <div className="inline-flex items-center gap-1 text-red-400 bg-red-400/10 px-2 py-0.5 rounded text-sm font-semibold mt-2"><TrendingDown className="w-4 h-4"/> Lower</div>;
        }
        return <div className="inline-flex items-center gap-1 text-blue-400 bg-blue-400/10 px-2 py-0.5 rounded text-sm font-semibold mt-2">Tie</div>;
    };

    return (
        <div className="flex flex-col gap-6 p-4 md:p-8 max-w-6xl mx-auto w-full">
            <div className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2">
                    <GitCompare className="w-8 h-8 text-primary" />
                    Compare Resumes
                </h1>
                <p className="text-muted-foreground">
                    A/B test two different resumes against a single Job Description to see which one performs better.
                </p>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Inputs Selection */}
                <div className="lg:col-span-1 flex flex-col gap-4">
                    <Card>
                        <CardHeader className="p-4">
                            <CardTitle className="text-lg text-primary">Job Description</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                            <Textarea 
                                placeholder="Paste the job description here..."
                                className="min-h-[150px] resize-y"
                                value={jd}
                                onChange={(e) => setJd(e.target.value)}
                            />
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="p-4">
                            <CardTitle className="text-lg text-indigo-500">Resume Version A</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                            <Textarea 
                                placeholder="Paste Resume A content..."
                                className="min-h-[120px] resize-y"
                                value={resumeA}
                                onChange={(e) => setResumeA(e.target.value)}
                            />
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="p-4">
                            <CardTitle className="text-lg text-purple-500">Resume Version B</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4 pt-0">
                            <Textarea 
                                placeholder="Paste Resume B content..."
                                className="min-h-[120px] resize-y"
                                value={resumeB}
                                onChange={(e) => setResumeB(e.target.value)}
                            />
                        </CardContent>
                    </Card>

                    <Button 
                        size="lg" 
                        onClick={handleCompare} 
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-md font-semibold h-12"
                    >
                        {loading ? <Loader2 className="mr-2 h-5 w-5 animate-spin" /> : <GitCompare className="mr-2 h-5 w-5" />}
                        {loading ? "Comparing..." : "Run Comparison"}
                    </Button>

                    {error && (
                        <div className="p-3 bg-red-500/10 border border-red-500/20 text-red-500 rounded-md text-sm">
                            {error}
                        </div>
                    )}
                </div>

                {/* Results Section */}
                <div className="lg:col-span-2 flex flex-col gap-6">
                    {!result && !loading && (
                        <Card className="h-full min-h-[400px] flex items-center justify-center border-dashed bg-muted/10">
                            <div className="text-center flex flex-col items-center gap-3">
                                <GitCompare className="w-12 h-12 text-muted-foreground/30" />
                                <p className="text-muted-foreground font-medium">Results will appear here</p>
                                <p className="text-sm text-muted-foreground/70 max-w-sm text-center">Paste 1 Job Description and 2 Resumes to let AI evaluate the better fit.</p>
                            </div>
                        </Card>
                    )}

                    {loading && (
                        <Card className="h-full min-h-[400px] flex items-center justify-center border-dashed">
                            <div className="text-center flex flex-col items-center gap-4">
                                <Loader2 className="w-10 h-10 text-primary animate-spin" />
                                <p className="text-muted-foreground animate-pulse">Running dual semantic analysis & AI evaluation...</p>
                            </div>
                        </Card>
                    )}

                    {result && (
                        <>
                            <div className="grid sm:grid-cols-2 gap-4">
                                <Card className={`border-2 ${result.score_a >= result.score_b ? 'border-primary shadow-primary/20 shadow-lg' : 'border-border'}`}>
                                    <CardHeader className="pb-2">
                                        <CardDescription>Version A Score</CardDescription>
                                        <CardTitle className="text-4xl">{result.score_a}%</CardTitle>
                                        {getWinnerIndicator(result.score_a, result.score_b)}
                                    </CardHeader>
                                </Card>
                                <Card className={`border-2 ${result.score_b > result.score_a ? 'border-primary shadow-primary/20 shadow-lg' : 'border-border'}`}>
                                    <CardHeader className="pb-2">
                                        <CardDescription>Version B Score</CardDescription>
                                        <CardTitle className="text-4xl">{result.score_b}%</CardTitle>
                                        {getWinnerIndicator(result.score_b, result.score_a)}
                                    </CardHeader>
                                </Card>
                            </div>

                            <Card className="flex-1 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 border-primary/20">
                                <CardHeader>
                                    <CardTitle className="flex items-center gap-2 text-indigo-500 text-xl font-bold">
                                        <Trophy className="w-5 h-5 text-indigo-500" />
                                        AI Recruiter Recommendation
                                    </CardTitle>
                                </CardHeader>
                                <CardContent>
                                    <div className="prose prose-sm dark:prose-invert max-w-none text-zinc-700 dark:text-zinc-300">
                                        <ReactMarkdown>{result.recommendation}</ReactMarkdown>
                                    </div>
                                </CardContent>
                            </Card>
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
