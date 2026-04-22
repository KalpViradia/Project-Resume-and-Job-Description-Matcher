"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Send, Loader2, Bot, User, FileText, X, Download } from "lucide-react";
import { cn } from "@/lib/utils";
import ReactMarkdown from "react-markdown";
import { jsPDF } from "jspdf";

interface Message {
    role: "user" | "model";
    text: string;
}

interface MatchContext {
    resumeText?: string;
    jobDescription?: string;
    matchScore?: number;
    matchedSkills?: string[];
    missingSkills?: string[];
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [matchContext, setMatchContext] = useState<MatchContext | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    // Load match context from localStorage on mount
    useEffect(() => {
        try {
            const stored = localStorage.getItem("matchContext");
            if (stored) {
                setMatchContext(JSON.parse(stored));
            }
        } catch {
            console.warn("Failed to parse match context");
        }
    }, []);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const buildContextString = (): string => {
        if (!matchContext) return "";

        const parts: string[] = [];

        if (matchContext.resumeText && matchContext.resumeText !== "(uploaded as file)") {
            // Truncate to ~2000 chars to stay within free-tier token limits
            const truncated = matchContext.resumeText.substring(0, 2000);
            parts.push(`RESUME:\n${truncated}${matchContext.resumeText.length > 2000 ? "\n...(truncated)" : ""}`);
        }

        if (matchContext.jobDescription) {
            const truncated = matchContext.jobDescription.substring(0, 2000);
            parts.push(`JOB DESCRIPTION:\n${truncated}${matchContext.jobDescription.length > 2000 ? "\n...(truncated)" : ""}`);
        }

        if (matchContext.matchScore !== undefined) {
            parts.push(`MATCH SCORE: ${matchContext.matchScore}%`);
        }

        if (matchContext.matchedSkills?.length) {
            parts.push(`MATCHED SKILLS: ${matchContext.matchedSkills.join(", ")}`);
        }

        if (matchContext.missingSkills?.length) {
            parts.push(`MISSING SKILLS: ${matchContext.missingSkills.join(", ")}`);
        }

        return parts.join("\n\n");
    };

    const clearContext = () => {
        setMatchContext(null);
        localStorage.removeItem("matchContext");
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg: Message = { role: "user", text: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setIsLoading(true);

        try {
            const history = messages.map(m => ({
                role: m.role,
                parts: [m.text]
            }));

            const contextString = buildContextString();

            const res = await fetch("http://localhost:8000/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: userMsg.text,
                    history: history,
                    context: contextString
                }),
            });

            if (!res.ok) {
                if (res.status === 429) {
                    throw new Error("RATE_LIMIT");
                }
                throw new Error("Failed to send message");
            }

            const data = await res.json();
            const botMsg: Message = { role: "model", text: data.response };
            setMessages((prev) => [...prev, botMsg]);
        } catch (error) {
            console.error(error);
            const errorMsg = error instanceof Error && error.message === "RATE_LIMIT"
                ? "⏳ Free API quota exceeded. Please wait about a minute and try again."
                : "Sorry, I encountered an error. Please try again.";
            setMessages((prev) => [...prev, { role: "model", text: errorMsg }]);
        } finally {
            setIsLoading(false);
        }
    };

    // Extract a short title from the JD for display
    const getJdTitle = () => {
        if (!matchContext?.jobDescription) return "Unknown Role";
        const firstLine = matchContext.jobDescription.split('\n')[0];
        return firstLine.substring(0, 50) + (firstLine.length > 50 ? "..." : "");
    };

    const exportChatToPDF = () => {
        const doc = new jsPDF();
        
        doc.setFontSize(22);
        doc.setTextColor("#4f46e5"); // Indigo
        doc.text("AI Career Consultation", 20, 20);
        
        doc.setFontSize(10);
        doc.setTextColor("#6b7280");
        doc.text(`Generated: ${new Date().toLocaleDateString()}`, 20, 28);
        
        if (matchContext) {
            doc.text(`Project Context: ${getJdTitle()}`, 20, 34);
            doc.text(`Match Score: ${matchContext.matchScore}%`, 20, 40);
        }

        doc.setLineWidth(0.5);
        doc.setDrawColor(200, 200, 200);
        doc.line(20, 45, 190, 45);

        let yPos = 55;
        doc.setFontSize(12);

        messages.filter(m => m.text).forEach((msg) => {
            const rolePrefix = msg.role === "user" ? "You:" : "AI Assistant:";
            doc.setFont("helvetica", "bold");
            doc.setTextColor(msg.role === "user" ? "#111827" : "#4f46e5");
            doc.text(rolePrefix, 20, yPos);
            yPos += 7;

            doc.setFont("helvetica", "normal");
            doc.setTextColor("#374151");
            
            // Clean up basic markdown for PDF (just a rough text output)
            const cleanText = msg.text.replace(/\*\*/g, '').replace(/###/g, '').replace(/\*/g, '-');
            
            const splitText = doc.splitTextToSize(cleanText, 170);
            
            // Check for page break
            if (yPos + (splitText.length * 6) > 280) {
                doc.addPage();
                yPos = 20;
            }

            doc.text(splitText, 20, yPos);
            yPos += (splitText.length * 6) + 10;
        });

        doc.save("Career-Chat-Export.pdf");
    };

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] p-4 max-w-5xl mx-auto w-full">
            <Card className="flex-1 flex flex-col shadow-sm border border-border/50 bg-background/50 backdrop-blur-sm">
                <div className="p-4 border-b flex flex-col bg-muted/20 gap-2">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <Bot className="h-5 w-5 text-primary" />
                            <h2 className="font-semibold text-lg">AI Career Assistant</h2>
                        </div>
                        {messages.length > 1 && (
                            <Button 
                                variant="outline" 
                                size="sm" 
                                className="h-8 gap-1 border-primary/20 hover:bg-primary/5 text-primary"
                                onClick={exportChatToPDF}
                            >
                                <Download className="h-3.5 w-3.5" />
                                Export PDF
                            </Button>
                        )}
                    </div>

                    {/* Context Banner */}
                    {matchContext ? (
                        <div className="flex items-center justify-between gap-2 bg-primary/10 p-2.5 rounded-lg border border-primary/20">
                            <div className="flex items-center gap-2 text-sm min-w-0">
                                <FileText className="h-4 w-4 text-primary shrink-0" />
                                <span className="text-primary font-medium shrink-0">Context loaded:</span>
                                <span className="text-muted-foreground truncate">{getJdTitle()}</span>
                                {matchContext.matchScore !== undefined && (
                                    <span className="text-xs bg-primary/20 text-primary px-2 py-0.5 rounded-full font-medium shrink-0">
                                        {matchContext.matchScore}% match
                                    </span>
                                )}
                            </div>
                            <Button variant="ghost" size="icon" className="h-6 w-6 shrink-0" onClick={clearContext} title="Clear context">
                                <X className="h-3 w-3" />
                            </Button>
                        </div>
                    ) : (
                        <p className="text-[10px] text-muted-foreground bg-yellow-500/10 p-2 rounded border border-yellow-500/20 text-center w-full">
                            No match context loaded. Go to Dashboard and run a match first to get personalized advice.
                        </p>
                    )}
                </div>

                <CardContent className="flex-1 overflow-y-auto p-6 space-y-6" ref={scrollRef}>
                    {messages.length === 0 && (
                        <div className="flex flex-col items-center justify-center h-full text-center space-y-4 text-muted-foreground opacity-50">
                            <Bot className="h-16 w-16" />
                            <div className="max-w-md">
                                <h3 className="text-xl font-medium mb-2">How can I help you today?</h3>
                                <p>
                                    {matchContext
                                        ? "I have your resume and job description context. Ask me for specific advice!"
                                        : "Ask me to review your resume, suggest skills, or provide interview tips."
                                    }
                                </p>
                            </div>
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <div
                            key={idx}
                            className={cn(
                                "flex gap-3 max-w-[85%]",
                                msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                            )}
                        >
                            <div className={cn(
                                "mt-1 h-8 w-8 rounded-full flex items-center justify-center shrink-0",
                                msg.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
                            )}>
                                {msg.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                            </div>

                            <div
                                className={cn(
                                    "rounded-2xl px-5 py-3 text-sm shadow-sm",
                                    msg.role === "user"
                                        ? "bg-primary text-primary-foreground rounded-tr-none"
                                        : "bg-card border border-border rounded-tl-none prose prose-sm dark:prose-invert max-w-none break-words"
                                )}
                            >
                                {msg.role === "user" ? (
                                    msg.text
                                ) : (
                                    <ReactMarkdown components={{
                                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="list-disc pl-4 mb-2 space-y-1" {...props} />,
                                        ol: ({ node, ...props }) => <ol className="list-decimal pl-4 mb-2 space-y-1" {...props} />,
                                        li: ({ node, ...props }) => <li className="" {...props} />,
                                        h1: ({ node, ...props }) => <h1 className="text-lg font-bold mb-2 mt-4" {...props} />,
                                        h2: ({ node, ...props }) => <h2 className="text-base font-bold mb-2 mt-3" {...props} />,
                                        h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-1 mt-2" {...props} />,
                                        code: ({ node, ...props }) => <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                                    }}>
                                        {msg.text}
                                    </ReactMarkdown>
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="flex gap-3 mr-auto">
                            <div className="mt-1 h-8 w-8 rounded-full bg-muted text-muted-foreground flex items-center justify-center shrink-0">
                                <Bot className="h-4 w-4" />
                            </div>
                            <div className="bg-card border border-border rounded-2xl rounded-tl-none px-5 py-3 shadow-sm flex items-center">
                                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground mr-2" />
                                <span className="text-sm text-muted-foreground">Thinking...</span>
                            </div>
                        </div>
                    )}
                </CardContent>

                <div className="p-4 border-t bg-background/50 backdrop-blur-sm">
                    <form
                        className="flex w-full gap-2 relative"
                        onSubmit={(e) => {
                            e.preventDefault();
                            handleSend();
                        }}
                    >
                        <Input
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder={matchContext ? "Ask about your match results..." : "Type instructions or specific keywords..."}
                            className="flex-1 pr-12 py-6"
                            disabled={isLoading}
                        />
                        <Button
                            type="submit"
                            size="icon"
                            className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8"
                            disabled={isLoading || !input.trim()}
                        >
                            <Send className="h-4 w-4" />
                        </Button>
                    </form>
                </div>
            </Card>
        </div>
    );
}
