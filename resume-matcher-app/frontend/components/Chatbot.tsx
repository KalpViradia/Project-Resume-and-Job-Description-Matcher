"use client";

import React, { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { MessageCircle, X, Send, Loader2, FileText } from "lucide-react";
import { cn } from "@/lib/utils";
import { usePathname } from "next/navigation";
import ReactMarkdown from "react-markdown";

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

export const Chatbot = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [matchContext, setMatchContext] = useState<MatchContext | null>(null);
    const scrollRef = useRef<HTMLDivElement>(null);
    const pathname = usePathname();

    // Reset chat on navigation
    useEffect(() => {
        setMessages([]);
    }, [pathname]);

    // Load match context from localStorage
    useEffect(() => {
        try {
            const stored = localStorage.getItem("matchContext");
            if (stored) {
                setMatchContext(JSON.parse(stored));
            }
        } catch {
            console.warn("Failed to parse match context");
        }
    }, [isOpen]); // Re-check when opened

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    const buildContextString = (): string => {
        if (!matchContext) return "";

        const parts: string[] = [];

        if (matchContext.resumeText && matchContext.resumeText !== "(uploaded as file)") {
            const truncated = matchContext.resumeText.substring(0, 1500);
            parts.push(`RESUME:\n${truncated}${matchContext.resumeText.length > 1500 ? "\n...(truncated)" : ""}`);
        }

        if (matchContext.jobDescription) {
            const truncated = matchContext.jobDescription.substring(0, 1500);
            parts.push(`JOB DESCRIPTION:\n${truncated}${matchContext.jobDescription.length > 1500 ? "\n...(truncated)" : ""}`);
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

    if (pathname === "/chat") {
        return null;
    }

    if (!isOpen) {
        return (
            <Button
                className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-xl z-50 p-0 bg-primary hover:bg-primary/90 transition-transform hover:scale-105"
                onClick={() => setIsOpen(true)}
            >
                <MessageCircle className="h-8 w-8 text-white" />
            </Button>
        );
    }

    return (
        <Card className="fixed bottom-6 right-6 w-[380px] h-[600px] shadow-2xl z-50 flex flex-col animate-in slide-in-from-bottom-5 fade-in duration-300 border-primary/20 bg-background">
            <CardHeader className="p-4 border-b bg-primary/5 flex flex-col space-y-2">
                <div className="flex flex-row items-center justify-between w-full">
                    <CardTitle className="text-lg font-bold flex items-center gap-2 text-primary">
                        <MessageCircle className="h-5 w-5" />
                        Resume Assistant
                    </CardTitle>
                    <div className="flex items-center gap-1">
                        <Button variant="ghost" size="icon" className="h-8 w-8" onClick={() => setIsOpen(false)}>
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                </div>
                {matchContext ? (
                    <div className="flex items-center gap-1.5 text-[10px] bg-primary/10 p-1.5 rounded border border-primary/20">
                        <FileText className="h-3 w-3 text-primary shrink-0" />
                        <span className="text-primary font-medium">Context active</span>
                        {matchContext.matchScore !== undefined && (
                            <span className="text-muted-foreground">• {matchContext.matchScore}% match</span>
                        )}
                    </div>
                ) : (
                    <p className="text-[10px] text-muted-foreground bg-yellow-500/10 p-2 rounded border border-yellow-500/20 text-center">
                        No context. Run a match on the Dashboard for personalized advice.
                    </p>
                )}
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4 space-y-4" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="text-center text-muted-foreground mt-4">
                        <p>
                            {matchContext
                                ? "I have your match context. Ask me for advice!"
                                : "Hi! I can help you improve your resume or answer career questions."
                            }
                        </p>
                    </div>
                )}
                {messages.map((msg, idx) => (
                    <div
                        key={idx}
                        className={cn(
                            "flex w-full",
                            msg.role === "user" ? "justify-end" : "justify-start"
                        )}
                    >
                        <div
                            className={cn(
                                "max-w-[80%] rounded-lg px-4 py-2 text-sm",
                                msg.role === "user"
                                    ? "bg-primary text-primary-foreground rounded-br-none"
                                    : "bg-muted text-muted-foreground rounded-bl-none prose prose-sm dark:prose-invert max-w-none"
                            )}
                        >
                            {msg.role === "user" ? (
                                msg.text
                            ) : (
                                <ReactMarkdown components={{
                                    p: ({ node, ...props }) => <p className="mb-1.5 last:mb-0 text-sm" {...props} />,
                                    ul: ({ node, ...props }) => <ul className="list-disc pl-3 mb-1.5 space-y-0.5 text-sm" {...props} />,
                                    ol: ({ node, ...props }) => <ol className="list-decimal pl-3 mb-1.5 space-y-0.5 text-sm" {...props} />,
                                    li: ({ node, ...props }) => <li className="text-sm" {...props} />,
                                    h1: ({ node, ...props }) => <h1 className="text-sm font-bold mb-1 mt-2" {...props} />,
                                    h2: ({ node, ...props }) => <h2 className="text-sm font-bold mb-1 mt-1.5" {...props} />,
                                    h3: ({ node, ...props }) => <h3 className="text-sm font-bold mb-0.5 mt-1" {...props} />,
                                    code: ({ node, ...props }) => <code className="bg-background/50 px-1 py-0.5 rounded text-xs font-mono" {...props} />,
                                }}>
                                    {msg.text}
                                </ReactMarkdown>
                            )}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex justify-start">
                        <div className="bg-muted rounded-lg px-4 py-2 rounded-bl-none">
                            <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                        </div>
                    </div>
                )}
            </CardContent>
            <CardFooter className="p-3 border-t bg-background">
                <form
                    className="flex w-full gap-2"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleSend();
                    }}
                >
                    <Input
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1"
                        disabled={isLoading}
                    />
                    <Button type="submit" size="icon" disabled={isLoading || !input.trim()}>
                        <Send className="h-4 w-4" />
                    </Button>
                </form>
            </CardFooter>
        </Card>
    );
};
