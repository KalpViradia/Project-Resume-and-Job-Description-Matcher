"use client";
import React from "react";
import { Card, CardHeader, CardContent, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { jsPDF } from "jspdf";
import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ResultsDashboardProps {
    matchScore: number;
    matchedSkills: string[];
    missingSkills: string[];
}

const CircularProgress = ({ value }: { value: number }) => {
    const radius = 50;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value / 100) * circumference;

    return (
        <div className="relative flex items-center justify-center">
            <svg className="transform -rotate-90 w-32 h-32">
                <circle
                    className="text-muted/20"
                    strokeWidth="8"
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx="64"
                    cy="64"
                />
                <circle
                    className="text-primary transition-all duration-1000 ease-in-out"
                    strokeWidth="8"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r={radius}
                    cx="64"
                    cy="64"
                />
            </svg>
            <span className="absolute text-2xl font-bold text-primary">{value}%</span>
        </div>
    );
};

export const ResultsDashboard = ({ matchScore, matchedSkills, missingSkills }: ResultsDashboardProps) => {
    const handleDownloadPDF = () => {
        const doc = new jsPDF();
        doc.setFontSize(20);
        doc.text("Match Report", 10, 10);

        doc.setFontSize(16);
        doc.text(`Match Score: ${matchScore}%`, 10, 30);

        doc.setFontSize(14);
        doc.text("Matched Skills:", 10, 50);
        doc.setFontSize(12);
        const matchedStr = matchedSkills.length > 0 ? matchedSkills.join(", ") : "None";
        const matchedLines = doc.splitTextToSize(matchedStr, 180);
        doc.text(matchedLines, 10, 60);

        const nextY = 60 + (matchedLines.length * 7);
        doc.setFontSize(14);
        doc.text("Missing Skills:", 10, nextY + 10);
        doc.setFontSize(12);
        const missingStr = missingSkills.length > 0 ? missingSkills.join(", ") : "None";
        const missingLines = doc.splitTextToSize(missingStr, 180);
        doc.text(missingLines, 10, nextY + 20);

        doc.save("match_report.pdf");
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8 animate-in fade-in slide-in-from-bottom-5 duration-700">
            {/* Score Card */}
            <Card className="col-span-1 border-none shadow-xl bg-gradient-to-br from-primary/5 to-secondary/10 relative overflow-hidden">
                <CardContent className="flex flex-col items-center justify-center py-10 gap-4">
                    <CircularProgress value={matchScore} />
                    <h3 className="text-xl font-bold text-foreground">Match Score</h3>
                    <Button
                        variant="default"
                        size="lg"
                        className="mt-6 flex items-center gap-3 px-6 py-3 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white rounded-lg shadow-lg"
                        onClick={handleDownloadPDF}
                    >
                        <Download className="w-5 h-5" /> Download PDF
                    </Button>
                </CardContent>
            </Card>

            {/* Skills Analysis */}
            <Card className="col-span-1 md:col-span-2 shadow-md">
                <CardHeader>
                    <CardTitle>Skills Analysis</CardTitle>
                    <CardDescription>Matched vs Missing Capabilities</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div>
                        <h4 className="text-sm font-semibold text-green-600 mb-3 flex items-center gap-2">
                            ✅ Matched Skills
                        </h4>
                        <div className="flex flex-wrap gap-2">
                            {matchedSkills.length > 0 ? matchedSkills.map(skill => (
                                <Badge key={skill} variant="secondary" className="px-3 py-1 bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400 border border-green-200 dark:border-green-800 hover:bg-green-200">
                                    {skill}
                                </Badge>
                            )) : <p className="text-sm text-muted-foreground">No matching skills found yet.</p>}
                        </div>
                    </div>

                    <div className="h-px bg-border my-4" />

                    <div>
                        <h4 className="text-sm font-semibold text-destructive mb-3 flex items-center gap-2">
                            ⚠️ Missing Skills
                        </h4>
                        <div className="flex flex-wrap gap-2">
                            {missingSkills.length > 0 ? missingSkills.map(skill => (
                                <div key={skill} className="flex items-center gap-2">
                                    <Badge variant="outline" className="px-3 py-1 border-destructive/20 text-destructive bg-destructive/5 hover:bg-destructive/10">
                                        {skill}
                                    </Badge>
                                    <a
                                        href={`https://www.google.com/search?q=learn+${encodeURIComponent(skill)}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="text-xs text-muted-foreground hover:text-primary underline decoration-dotted"
                                    >
                                        Learn
                                    </a>
                                </div>
                            )) : <p className="text-sm text-muted-foreground">Great! No critical skills missing.</p>}
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
};
