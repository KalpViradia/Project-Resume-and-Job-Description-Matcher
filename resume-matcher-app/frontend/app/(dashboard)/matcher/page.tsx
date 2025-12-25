"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { ResumeUploader } from "@/components/ResumeUploader";
import { ResultsDashboard } from "@/components/ResultsDashboard";
import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Loader2 } from "lucide-react";

export default function MatcherPage() {
    const [jd, setJd] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [resumeText, setResumeText] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [matchResult, setMatchResult] = useState<{ score: number, matched: string[], missing: string[] } | null>(null);
    const [showError, setShowError] = useState(false);

    const handleMatch = async () => {
        setIsLoading(true);
        setMatchResult(null);

        // Create FormData
        const formData = new FormData();
        if (file) {
            formData.append("resume", file);
        } else if (resumeText) {
            formData.append("resume_text_input", resumeText);
        } else {
            // Handle case where no file is selected but we enabled button (should check disabled prop)
            setIsLoading(false);
            return;
        }
        formData.append("jd_text", jd);

        try {
            const res = await fetch("http://localhost:8000/match", {
                method: "POST",
                body: formData,
            });

            if (!res.ok) {
                throw new Error("Failed to match");
            }

            const data = await res.json(); // { match_score, matched_skills, missing_skills }

            const result = {
                score: data.match_score,
                matched: data.matched_skills,
                missing: data.missing_skills
            };

            setMatchResult(result);

            // Save to history using Node API
            const token = localStorage.getItem("token");
            // Only attempt to save if we have a seemingly valid token
            if (token && token !== "undefined" && token !== "null") {
                try {
                    const historyRes = await fetch("http://localhost:5000/api/history", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "x-auth-token": token,
                        },
                        body: JSON.stringify({
                            jobDescription: jd,
                            matchScore: result.score,
                            matchedSkills: result.matched,
                            missingSkills: result.missing,
                        }),
                    });

                    if (!historyRes.ok) {
                        // If 401/403, might be expired token. Clear it so next time we treat as public.
                        if (historyRes.status === 401 || historyRes.status === 403) {
                            console.warn("Token expired or invalid during save. Clearing token.");
                            localStorage.removeItem("token");
                            // Optionally redirect or just let them stay as guest
                        } else {
                            // Genuine error for logged in user
                            throw new Error("Failed to save history");
                        }
                    }
                } catch (e) {
                    console.error("Failed to save history", e);
                    // Only show alert if we REALLY thought we were logged in (token existed)
                    // and it wasn't just an auth error we handled above.
                    setShowError(true);
                }
            }
        } catch (error) {
            console.error("Match error:", error);
            setShowError(true);
        } finally {
            setIsLoading(false);
            if (matchResult && matchResult.score > 80) {
                // @ts-ignore
                import("canvas-confetti").then((confetti) => {
                    confetti.default({
                        particleCount: 100,
                        spread: 70,
                        origin: { y: 0.6 }
                    });
                });
            }

            if (matchResult) {
                // Update persistent storage AND active context
                const contextPayload = {
                    jobDescription: jd,
                    matchScore: matchResult.score,
                    missingSkills: matchResult.missing
                };
                localStorage.setItem("chatContext", JSON.stringify(contextPayload));

                // We need to access setContextData here, but we can't use hooks inside handleMatch (callback).
                // valid strategy: invoke a useEffect that watches matchResult? 
                // OR just call the function if we hoist it.
                // But handleMatch is inside the component, so we CAN use the hook's return value.
            }
        }
    };

    // Use the context hook
    // const { setContextData } = useChat();

    // Effect to update chat context when matchResult changes
    // useEffect(() => {
    //     if (matchResult) {
    //         setContextData({
    //             jobDescription: jd,
    //             matchScore: matchResult.score,
    //             missingSkills: matchResult.missing
    //         });
    //     }
    // }, [matchResult, jd, setContextData]);

    return (
        <div className="space-y-8 animate-in fade-in duration-500 max-w-6xl mx-auto">
            <header className="flex flex-col gap-2">
                <h1 className="text-3xl font-bold tracking-tight text-primary">Resume Matcher</h1>
                <p className="text-muted-foreground">Upload your resume and paste the job description to get a detailed match analysis.</p>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                {/* Resume Section */}
                <Card className="shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3">
                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">1</span>
                            Upload Resume
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="h-[600px] flex flex-col gap-4">
                        {/* Upload section */}
                        <div className="flex-shrink-0">
                            <ResumeUploader onFileSelect={setFile} />
                        </div>

                        {/* Divider */}
                        <div className="relative">
                            <div className="absolute inset-0 flex items-center">
                                <span className="w-full border-t" />
                            </div>
                            <div className="relative flex justify-center text-xs uppercase">
                                <span className="bg-background px-2 text-muted-foreground">Or paste text</span>
                            </div>
                        </div>

                        {/* Textarea grows as needed */}
                        <Textarea
                            placeholder="Paste Resume Text..."
                            className="flex-1 min-h-[100px] max-h-[500px] font-mono resize-none focus-visible:ring-primary overflow-auto"
                            value={resumeText}
                            onChange={(e) => setResumeText(e.target.value)}
                        />
                    </CardContent>
                </Card>

                {/* JD Section */}
                <Card className="shadow-sm hover:shadow-md transition-shadow">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-3">
                            <span className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary text-sm font-bold text-secondary-foreground">2</span>
                            Job Description
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Textarea
                            placeholder="Paste Job Description e.g. We are looking for a Senior React Developer..."
                            className="min-h-[600px] font-mono resize-none focus-visible:ring-primary"
                            value={jd}
                            onChange={(e) => setJd(e.target.value)}
                        />
                    </CardContent>
                </Card>
            </div>

            <div className="flex flex-col items-center justify-center py-8">
                <Button
                    size="lg"
                    className="px-8 py-6 text-lg font-bold shadow-lg shadow-primary/25 min-w-[200px]"
                    onClick={handleMatch}
                    disabled={isLoading || ((!file && !resumeText) || !jd)}
                >
                    {isLoading ? (
                        <>
                            <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                            Analyzing...
                        </>
                    ) : (
                        "Analyze & Match"
                    )}
                </Button>

                {matchResult && (
                    <div className="w-full">
                        <ResultsDashboard
                            matchScore={matchResult.score}
                            matchedSkills={matchResult.matched}
                            missingSkills={matchResult.missing}
                        />
                    </div>
                )}
            </div>

            <AlertDialog open={showError} onOpenChange={setShowError}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Error</AlertDialogTitle>
                        <AlertDialogDescription>
                            We matched your resume but failed to save it to your history. Please check your connection.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogAction onClick={() => setShowError(false)}>OK</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </div>
    )
}
