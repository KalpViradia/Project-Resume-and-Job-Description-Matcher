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
    improvementSuggestions?: string[];
}

const CircularProgress = ({ value }: { value: number }) => {
    const radius = 50;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (value / 100) * circumference;

    // Color based on score
    const getColor = () => {
        if (value >= 80) return "text-green-500";
        if (value >= 60) return "text-yellow-500";
        if (value >= 40) return "text-orange-500";
        return "text-red-500";
    };

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
                    className={`${getColor()} transition-all duration-1000 ease-in-out`}
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
            <span className={`absolute text-2xl font-bold ${getColor()}`}>{value}%</span>
        </div>
    );
};

export const ResultsDashboard = ({ matchScore, matchedSkills, missingSkills, improvementSuggestions = [] }: ResultsDashboardProps) => {
    const handleDownloadPDF = () => {
        const doc = new jsPDF();
        const pageWidth = doc.internal.pageSize.getWidth();
        const margin = 15;
        const contentWidth = pageWidth - margin * 2;
        let y = margin;

        // --- Header ---
        doc.setFillColor(37, 99, 235); // Blue header bar
        doc.rect(0, 0, pageWidth, 35, 'F');

        doc.setTextColor(255, 255, 255);
        doc.setFontSize(22);
        doc.setFont("helvetica", "bold");
        doc.text("Resume Match Report", margin, 22);

        doc.setFontSize(9);
        doc.setFont("helvetica", "normal");
        doc.text(`Generated on ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}`, margin, 30);

        y = 50;

        // --- Match Score Section ---
        doc.setTextColor(0, 0, 0);
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("Match Score", margin, y);
        y += 8;

        // Score badge
        const scoreColor = matchScore >= 80 ? [34, 197, 94] : matchScore >= 60 ? [234, 179, 8] : matchScore >= 40 ? [249, 115, 22] : [239, 68, 68];
        doc.setFillColor(scoreColor[0], scoreColor[1], scoreColor[2]);
        doc.roundedRect(margin, y, 50, 14, 3, 3, 'F');
        doc.setTextColor(255, 255, 255);
        doc.setFontSize(16);
        doc.setFont("helvetica", "bold");
        doc.text(`${matchScore}%`, margin + 25, y + 10, { align: "center" });

        const scoreLabel = matchScore >= 80 ? "Excellent Match" : matchScore >= 60 ? "Good Match" : matchScore >= 40 ? "Fair Match" : "Poor Match";
        doc.setTextColor(100, 100, 100);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");
        doc.text(scoreLabel, margin + 55, y + 10);

        y += 28;

        // --- Divider ---
        doc.setDrawColor(220, 220, 220);
        doc.line(margin, y, pageWidth - margin, y);
        y += 12;

        // --- Matched Skills ---
        doc.setTextColor(34, 197, 94);
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.text("✓ Matched Skills", margin, y);
        y += 8;

        doc.setTextColor(60, 60, 60);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");

        if (matchedSkills.length > 0) {
            const matchedStr = matchedSkills.join("  •  ");
            const matchedLines = doc.splitTextToSize(matchedStr, contentWidth);
            doc.text(matchedLines, margin, y);
            y += matchedLines.length * 5 + 5;
        } else {
            doc.setTextColor(150, 150, 150);
            doc.text("No matching skills found.", margin, y);
            y += 8;
        }

        y += 8;

        // --- Divider ---
        doc.setDrawColor(220, 220, 220);
        doc.line(margin, y, pageWidth - margin, y);
        y += 12;

        // --- Missing Skills ---
        doc.setTextColor(239, 68, 68);
        doc.setFontSize(13);
        doc.setFont("helvetica", "bold");
        doc.text("✗ Missing Skills", margin, y);
        y += 8;

        doc.setTextColor(60, 60, 60);
        doc.setFontSize(10);
        doc.setFont("helvetica", "normal");

        if (missingSkills.length > 0) {
            const missingStr = missingSkills.join("  •  ");
            const missingLines = doc.splitTextToSize(missingStr, contentWidth);
            doc.text(missingLines, margin, y);
            y += missingLines.length * 5 + 5;
        } else {
            doc.setTextColor(34, 197, 94);
            doc.text("No critical skills missing!", margin, y);
            y += 8;
        }

        y += 15;

        // --- Footer ---
        doc.setDrawColor(220, 220, 220);
        doc.line(margin, y, pageWidth - margin, y);
        y += 8;
        doc.setTextColor(150, 150, 150);
        doc.setFontSize(8);
        doc.text("AI Resume Matcher — Powered by BERT & Gemini AI", margin, y);

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
                    
                    {improvementSuggestions.length > 0 && (
                        <>
                            <div className="h-px bg-border my-4" />
                            <div>
                                <h4 className="text-sm font-semibold text-blue-600 dark:text-blue-400 mb-3 flex items-center gap-2">
                                    💡 Improvement Suggestions
                                </h4>
                                <ul className="list-disc list-inside space-y-1">
                                    {improvementSuggestions.map((suggestion, idx) => (
                                        <li key={idx} className="text-sm text-muted-foreground">{suggestion}</li>
                                    ))}
                                </ul>
                            </div>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};
